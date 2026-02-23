"""Wrapper for the vmcli command-line tool shipped with VMware Fusion."""
import subprocess


class VMwareCLI:
    """
    Wrapper for the vmcli CLI that ships alongside VMware Fusion.

    vmcli exposes functionality not available through vmrun, including VM
    creation, chipset configuration, disk management, ethernet setup,
    display/keyboard control (MKS), guest operations, shared folder
    fine-tuning (HGFS), VMware Tools upgrade, VM templates, VProbes, and
    arbitrary VMX config-param access.

    Usage::

        import shutil
        from vmware_fusion_py import VMwareCLI

        vmcli = VMwareCLI(
            vmcli_path=shutil.which("vmcli"),
            vm_path="/path/to/vm.vmx",
            guest_user="user",
            guest_password="pass",
        )
        vmcli.set_vcpu_count(4)
        vmcli.set_mem_size(8192)
    """

    def __init__(
        self,
        vmcli_path: str,
        vm_path: str = None,
        guest_user: str = None,
        guest_password: str = None,
        verbose: bool = False,
    ) -> None:
        self.vmcli_path = vmcli_path
        self.vm_path = vm_path
        self.guest_user = guest_user
        self.guest_password = guest_password
        self.verbose = verbose

    def _run_command(self, module, command, vm_path=None, args=None):
        """Build and execute a vmcli command.

        Command shape: vmcli [<vmx>] <module> <command> [<args>] [--verbose]
        """
        cmd = [self.vmcli_path]
        effective_vm_path = vm_path or self.vm_path
        if effective_vm_path:
            cmd.append(effective_vm_path)
        cmd.extend([module, command])
        if args:
            cmd.extend(str(a) for a in args)
        if self.verbose:
            cmd.append("--verbose")
        try:
            with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                stdout, stderr = proc.communicate()
                return {
                    "return_code": proc.returncode,
                    "output": stdout.decode("utf-8").strip(),
                    "error": stderr.decode("utf-8").strip(),
                }
        except FileNotFoundError:
            return {"return_code": 2, "output": "", "error": "vmcli not found"}

    # ------------------------------------------------------------------
    # VM
    # ------------------------------------------------------------------

    def create_vm(self, name, dirpath, guest_type=None, custom_guest_type=None):
        """
        Create a new VM.

        :param name: VM display name
        :param dirpath: Directory where the VM will be created
        :param guest_type: Guest OS type (e.g. ``arm-ubuntu-64``)
        :param custom_guest_type: Any other guest OS type string
        :return: Command result dict
        """
        args = ["-n", name, "-d", dirpath]
        if guest_type:
            args.extend(["-g", guest_type])
        if custom_guest_type:
            args.extend(["-c", custom_guest_type])
        return self._run_command("VM", "Create", vm_path=None, args=args)

    # ------------------------------------------------------------------
    # Chipset
    # ------------------------------------------------------------------

    def query_chipset(self, vm_path=None):
        """Query chipset state (vCPU count, memory, etc.)."""
        return self._run_command("Chipset", "query", vm_path=vm_path)

    def set_vcpu_count(self, vcpus, vm_path=None):
        """
        Set the number of virtual CPUs.

        :param vcpus: Number of vCPUs
        :param vm_path: Path to the VMX file (falls back to instance vm_path)
        """
        return self._run_command("Chipset", "SetVCpuCount", vm_path=vm_path, args=[str(vcpus)])

    def set_mem_size(self, size_mb, vm_path=None):
        """
        Set memory size in MB.

        :param size_mb: Memory in megabytes
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Chipset", "SetMemSize", vm_path=vm_path, args=[str(size_mb)])

    def set_cores_per_socket(self, cores, vm_path=None):
        """
        Set cores per socket.

        :param cores: Number of cores per socket
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Chipset", "SetCoresPerSocket", vm_path=vm_path, args=[str(cores)])

    def set_simultaneous_threads(self, threads, vm_path=None):
        """
        Set simultaneous threads (SMT/hyperthreading) per vCPU.

        :param threads: Number of threads per vCPU
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Chipset", "SetSimultaneousThreads", vm_path=vm_path, args=[str(threads)])

    # ------------------------------------------------------------------
    # Disk
    # ------------------------------------------------------------------

    def query_disks(self, vm_path=None):
        """Query the disk configuration of the VM."""
        return self._run_command("Disk", "query", vm_path=vm_path)

    def create_disk(self, filepath, adapter, size, disk_type, vm_path=None):
        """
        Create a virtual disk file.

        :param filepath: Full path for the new ``.vmdk`` file
        :param adapter: Adapter type: ``ide``, ``buslogic``, or ``lsilogic``
        :param size: Capacity string, e.g. ``20GB`` or ``10240MB``
        :param disk_type: 0=single growable, 1=growable split, 2=preallocated, 3=preallocated split
        :param vm_path: Path to the VMX file
        """
        args = ["-f", filepath, "-a", adapter, "-s", size, "-t", str(disk_type)]
        return self._run_command("Disk", "Create", vm_path=vm_path, args=args)

    def extend_disk(self, disk_label, new_num_sectors, vm_path=None):
        """
        Extend a virtual disk.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param new_num_sectors: Desired size in sectors
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Disk", "Extend", vm_path=vm_path, args=[disk_label, str(new_num_sectors)])

    def move_disk(self, from_label, to_label, vm_path=None):
        """
        Move a disk from one slot to another.

        :param from_label: Source device label, e.g. ``scsi0:0``
        :param to_label: Destination device label
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Disk", "Move", vm_path=vm_path, args=[from_label, to_label])

    def branch_disk(self, disk_label, vm_path=None):
        """
        Create a disk branch based on the current VM state.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Disk", "Branch", vm_path=vm_path, args=[disk_label])

    def disk_connection_control(self, disk_label, connected, vm_path=None):
        """
        Connect or disconnect a disk device.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param connected: ``True`` to connect, ``False`` to disconnect
        :param vm_path: Path to the VMX file
        """
        state = "true" if connected else "false"
        return self._run_command("Disk", "ConnectionControl", vm_path=vm_path, args=[disk_label, state])

    # ------------------------------------------------------------------
    # Ethernet
    # ------------------------------------------------------------------

    def query_ethernet(self, vm_path=None):
        """Query ethernet adapter configuration."""
        return self._run_command("Ethernet", "query", vm_path=vm_path)

    def set_ethernet_connection_type(self, device_label, connection_type, vm_path=None):
        """
        Set the connection type for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param connection_type: Connection type string (e.g. ``bridged``, ``nat``, ``hostonly``)
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Ethernet", "SetConnectionType", vm_path=vm_path, args=[device_label, connection_type])

    def set_ethernet_security_policy(self, device_label, no_promisc, down_when_addr_mismatch, no_forged_src_addr, vm_path=None):
        """
        Set the security policy for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param no_promisc: Disable promiscuous mode (bool)
        :param down_when_addr_mismatch: Bring link down on address mismatch (bool)
        :param no_forged_src_addr: Disallow forged source addresses (bool)
        :param vm_path: Path to the VMX file
        """
        def _b(v):
            return "true" if v else "false"
        args = [device_label, _b(no_promisc), _b(down_when_addr_mismatch), _b(no_forged_src_addr)]
        return self._run_command("Ethernet", "SetSecurityPolicy", vm_path=vm_path, args=args)

    def set_ethernet_network_name(self, device_label, network_name, vm_path=None):
        """
        Set the network name for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param network_name: Name of the host network
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Ethernet", "SetNetworkName", vm_path=vm_path, args=[device_label, network_name])

    def ethernet_connection_control(self, device_label, connected, vm_path=None):
        """
        Connect or disconnect an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param connected: ``True`` to connect, ``False`` to disconnect
        :param vm_path: Path to the VMX file
        """
        state = "true" if connected else "false"
        return self._run_command("Ethernet", "ConnectionControl", vm_path=vm_path, args=[device_label, state])

    # ------------------------------------------------------------------
    # MKS (display / keyboard / screen)
    # ------------------------------------------------------------------

    def query_mks(self, vm_path=None):
        """Query MKS (display and keyboard) state."""
        return self._run_command("MKS", "query", vm_path=vm_path)

    def capture_screenshot(self, filename, vm_path=None):
        """
        Capture a screenshot of the guest display.

        :param filename: Output file path on the host
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "captureScreenshot", vm_path=vm_path, args=[filename])

    def send_key_event(self, hidcode, modifier, vm_path=None):
        """
        Send a single key event to the guest.

        :param hidcode: HID usage code for the key
        :param modifier: Modifier flags (e.g. 0 for none)
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "sendKeyEvent", vm_path=vm_path, args=[str(hidcode), str(modifier)])

    def send_key_sequence(self, sequence, vm_path=None):
        """
        Send a key sequence to the guest.

        :param sequence: Key sequence string
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "sendKeySequence", vm_path=vm_path, args=[sequence])

    def set_guest_resolution(self, width, height, vm_path=None):
        """
        Set the guest display resolution.

        :param width: Width in pixels
        :param height: Height in pixels
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "SetGuestResolution", vm_path=vm_path, args=[str(width), str(height)])

    def set_num_displays(self, count, vm_path=None):
        """
        Set the number of displays in the VM.

        :param count: Number of displays
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "SetNumDisplays", vm_path=vm_path, args=[str(count)])

    def set_3d_accel(self, enabled, vm_path=None):
        """
        Enable or disable 3D acceleration.

        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "SetAccel3d", vm_path=vm_path, args=["true" if enabled else "false"])

    def set_vram_size(self, size_mb, vm_path=None):
        """
        Set the VRAM size.

        :param size_mb: VRAM size in MB
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "SetVramSize", vm_path=vm_path, args=[str(size_mb)])

    def set_graphics_memory(self, size_kb, vm_path=None):
        """
        Set graphics memory size in kilobytes.

        :param size_kb: Graphics memory in KB
        :param vm_path: Path to the VMX file
        """
        return self._run_command("MKS", "SetGraphicsMemoryKB", vm_path=vm_path, args=[str(size_kb)])

    # ------------------------------------------------------------------
    # ConfigParams
    # ------------------------------------------------------------------

    def query_config(self, vm_path=None):
        """Read all VMX configuration parameters."""
        return self._run_command("ConfigParams", "query", vm_path=vm_path)

    def set_config_entry(self, name, value, vm_path=None):
        """
        Write an arbitrary VMX configuration entry.

        :param name: Config key name
        :param value: Config key value
        :param vm_path: Path to the VMX file
        """
        return self._run_command("ConfigParams", "SetEntry", vm_path=vm_path, args=[name, value])

    # ------------------------------------------------------------------
    # HGFS (shared folders)
    # ------------------------------------------------------------------

    def query_hgfs(self, vm_path=None):
        """Query HGFS shared folder state."""
        return self._run_command("HGFS", "query", vm_path=vm_path)

    def set_share_enabled(self, share_label, enabled, vm_path=None):
        """
        Enable or disable a shared folder.

        :param share_label: Share label
        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetEnabled", vm_path=vm_path, args=[share_label, "true" if enabled else "false"])

    def set_share_read_access(self, share_label, readable, vm_path=None):
        """
        Set read access for a shared folder.

        :param share_label: Share label
        :param readable: ``True`` to allow reads
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetReadAccess", vm_path=vm_path, args=[share_label, "true" if readable else "false"])

    def set_share_write_access(self, share_label, writable, vm_path=None):
        """
        Set write access for a shared folder.

        :param share_label: Share label
        :param writable: ``True`` to allow writes
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetWriteAccess", vm_path=vm_path, args=[share_label, "true" if writable else "false"])

    def set_share_follow_symlinks(self, share_label, follow, vm_path=None):
        """
        Configure whether symlinks are followed in a shared folder.

        :param share_label: Share label
        :param follow: ``True`` to follow symlinks
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetFollowSymlinks", vm_path=vm_path, args=[share_label, "true" if follow else "false"])

    def set_share_host_path(self, share_label, host_path, vm_path=None):
        """
        Set the host-side path for a shared folder.

        :param share_label: Share label
        :param host_path: Absolute host path
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetHostPath", vm_path=vm_path, args=[share_label, host_path])

    def set_share_guest_name(self, share_label, guest_name, vm_path=None):
        """
        Set the name by which the guest sees a shared folder.

        :param share_label: Share label
        :param guest_name: Name visible inside the guest
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetGuestName", vm_path=vm_path, args=[share_label, guest_name])

    def set_share_present(self, share_label, present, vm_path=None):
        """
        Mark a shared folder as present or absent.

        :param share_label: Share label
        :param present: ``True`` to mark as present
        :param vm_path: Path to the VMX file
        """
        return self._run_command("HGFS", "SetPresent", vm_path=vm_path, args=[share_label, "true" if present else "false"])

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def install_tools(self, vm_path=None):
        """Mount the VMware Tools installer ISO in the guest."""
        return self._run_command("Tools", "Install", vm_path=vm_path)

    def upgrade_tools(self, cmdline=None, backing_type=None, backing_path=None, vm_path=None):
        """
        Upgrade VMware Tools inside the guest.

        :param cmdline: Command line arguments for the upgrade installer
        :param backing_type: Backing type (0, 1, or 2)
        :param backing_path: Path to the tools installer
        :param vm_path: Path to the VMX file
        """
        args = []
        if cmdline:
            args.extend(["-c", cmdline])
        if backing_type is not None:
            args.extend(["-bt", str(backing_type)])
        if backing_path:
            args.extend(["-bp", backing_path])
        return self._run_command("Tools", "Upgrade", vm_path=vm_path, args=args or None)

    def query_tools(self, vm_path=None):
        """Query VMware Tools installation state."""
        return self._run_command("Tools", "Query", vm_path=vm_path)

    # ------------------------------------------------------------------
    # VMTemplate
    # ------------------------------------------------------------------

    def create_template(self, template_path, name, source_vmx=None):
        """
        Create a VM template from a VMX file.

        :param template_path: Destination ``.vmtx`` file path
        :param name: Template display name
        :param source_vmx: Source VMX file (can also be set via vm_path)
        """
        args = ["-p", template_path, "-n", name]
        return self._run_command("VMTemplate", "Create", vm_path=source_vmx, args=args)

    def deploy_template(self, template_path):
        """
        Deploy a VM from a template.

        :param template_path: Path to the ``.vmtx`` template file
        """
        args = ["-p", template_path]
        return self._run_command("VMTemplate", "Deploy", vm_path=None, args=args)

    # ------------------------------------------------------------------
    # VProbes
    # ------------------------------------------------------------------

    def query_vprobes(self, vm_path=None):
        """Query VProbes state."""
        return self._run_command("VProbes", "Query", vm_path=vm_path)

    def load_vprobes(self, script, vm_path=None):
        """
        Load a VProbes script onto the VM.

        :param script: Path to the VProbes script file
        :param vm_path: Path to the VMX file
        """
        return self._run_command("VProbes", "Load", vm_path=vm_path, args=[script])

    def reset_vprobes(self, vm_path=None):
        """Disable all active VProbes on the VM."""
        return self._run_command("VProbes", "Reset", vm_path=vm_path)

    def set_vprobes_enabled(self, enabled, vm_path=None):
        """
        Enable or disable VProbes on the VM.

        :param enabled: ``True`` to enable VProbes
        :param vm_path: Path to the VMX file
        """
        return self._run_command("VProbes", "SetEnabled", vm_path=vm_path, args=["true" if enabled else "false"])

    # ------------------------------------------------------------------
    # Guest (guest ops via VMware Tools)
    # ------------------------------------------------------------------

    def _guest_args(self, extra=None):
        """Build the common -u/-p credential args for Guest commands."""
        args = []
        if self.guest_user:
            args.extend(["-u", self.guest_user])
        if self.guest_password:
            args.extend(["-p", self.guest_password])
        if extra:
            args.extend(extra)
        return args

    def query_guest(self, vm_path=None):
        """Query guest state."""
        return self._run_command("Guest", "query", vm_path=vm_path)

    def guest_ls(self, path, vm_path=None):
        """
        List directory contents in the guest.

        :param path: Guest path to list
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "ls", vm_path=vm_path, args=self._guest_args([path]))

    def guest_mkdir(self, path, vm_path=None):
        """
        Create a directory in the guest.

        :param path: Guest path to create
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "mkdir", vm_path=vm_path, args=self._guest_args([path]))

    def guest_rm(self, path, vm_path=None):
        """
        Remove a file in the guest.

        :param path: Guest file path to remove
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "rm", vm_path=vm_path, args=self._guest_args([path]))

    def guest_rmdir(self, path, vm_path=None):
        """
        Remove a directory in the guest.

        :param path: Guest directory path to remove
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "rmdir", vm_path=vm_path, args=self._guest_args([path]))

    def guest_mv(self, src, dst, vm_path=None):
        """
        Move/rename a file in the guest.

        :param src: Source guest path
        :param dst: Destination guest path
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "mv", vm_path=vm_path, args=self._guest_args([src, dst]))

    def guest_mvdir(self, src, dst, vm_path=None):
        """
        Move a directory in the guest.

        :param src: Source guest path
        :param dst: Destination guest path
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "mvdir", vm_path=vm_path, args=self._guest_args([src, dst]))

    def guest_ps(self, pid=None, vm_path=None):
        """
        List running processes in the guest.

        :param pid: Filter by PID (optional)
        :param vm_path: Path to the VMX file
        """
        extra = []
        if pid is not None:
            extra.extend(["-pid", str(pid)])
        return self._run_command("Guest", "ps", vm_path=vm_path, args=self._guest_args(extra))

    def guest_kill(self, pid, vm_path=None):
        """
        Kill a process in the guest.

        :param pid: PID to kill
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "kill", vm_path=vm_path, args=self._guest_args([str(pid)]))

    def guest_run(
        self,
        program,
        program_args=None,
        no_wait=False,
        activate_window=False,
        interactive=False,
        working_dir=None,
        environment=None,
        vm_path=None,
    ):
        """
        Start a program inside the guest.

        :param program: Path to the program inside the guest
        :param program_args: List of arguments to pass to the program
        :param no_wait: Return immediately without waiting for completion
        :param activate_window: Activate the program window after start
        :param interactive: Force interactive guest login
        :param working_dir: Working directory inside the guest
        :param environment: Environment variable string
        :param vm_path: Path to the VMX file
        """
        extra = []
        if no_wait:
            extra.append("-nw")
        if activate_window:
            extra.append("-aw")
        if interactive:
            extra.append("-i")
        if working_dir:
            extra.extend(["-w", working_dir])
        if environment:
            extra.extend(["-e", environment])
        extra.append(program)
        if program_args:
            extra.extend(program_args)
        return self._run_command("Guest", "run", vm_path=vm_path, args=self._guest_args(extra))

    def guest_copy_from(self, guest_path, host_path, vm_path=None):
        """
        Copy a file from the guest to the host.

        :param guest_path: Source path inside the guest
        :param host_path: Destination path on the host
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "copyFrom", vm_path=vm_path, args=self._guest_args([guest_path, host_path]))

    def guest_copy_to(self, host_path, guest_path, vm_path=None):
        """
        Copy a file from the host to the guest.

        :param host_path: Source path on the host
        :param guest_path: Destination path inside the guest
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Guest", "copyTo", vm_path=vm_path, args=self._guest_args([host_path, guest_path]))

    def guest_create_temp_dir(self, vm_path=None):
        """Create a temporary directory in the guest."""
        return self._run_command("Guest", "createTempDir", vm_path=vm_path, args=self._guest_args())

    def guest_create_temp_file(self, vm_path=None):
        """Create a temporary file in the guest."""
        return self._run_command("Guest", "createTempFile", vm_path=vm_path, args=self._guest_args())

    def guest_env(self, vm_path=None):
        """List environment variables in the guest."""
        return self._run_command("Guest", "env", vm_path=vm_path, args=self._guest_args())

    # ------------------------------------------------------------------
    # Power (vmcli native power control)
    # ------------------------------------------------------------------

    def query_power(self, vm_path=None):
        """Query the current power state of the VM."""
        return self._run_command("Power", "query", vm_path=vm_path)

    def power_start(self, vm_path=None):
        """Start the VM."""
        return self._run_command("Power", "Start", vm_path=vm_path)

    def power_stop(self, vm_path=None):
        """Stop the VM."""
        return self._run_command("Power", "Stop", vm_path=vm_path)

    def power_pause(self, vm_path=None):
        """Pause the VM."""
        return self._run_command("Power", "Pause", vm_path=vm_path)

    def power_reset(self, vm_path=None):
        """Reset the VM."""
        return self._run_command("Power", "Reset", vm_path=vm_path)

    def power_suspend(self, vm_path=None):
        """Suspend the VM."""
        return self._run_command("Power", "Suspend", vm_path=vm_path)

    def power_unpause(self, vm_path=None):
        """Unpause the VM."""
        return self._run_command("Power", "Unpause", vm_path=vm_path)

    # ------------------------------------------------------------------
    # Snapshot (vmcli native snapshot control)
    # ------------------------------------------------------------------

    def query_snapshots(self, vm_path=None):
        """Query snapshot configuration."""
        return self._run_command("Snapshot", "query", vm_path=vm_path)

    def take_snapshot(self, name, vm_path=None):
        """
        Take a snapshot of the VM.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Snapshot", "Take", vm_path=vm_path, args=[name])

    def delete_snapshot(self, name, vm_path=None):
        """
        Delete a snapshot from the VM.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Snapshot", "Delete", vm_path=vm_path, args=[name])

    def revert_snapshot(self, name, vm_path=None):
        """
        Revert the VM to a snapshot.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Snapshot", "Revert", vm_path=vm_path, args=[name])

    def clone_snapshot(self, name, vm_path=None):
        """
        Clone from a snapshot.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run_command("Snapshot", "Clone", vm_path=vm_path, args=[name])

"""Wrapper for the vmcli command-line tool shipped with VMware Fusion."""

import subprocess


def _b(v):
    """Convert a bool to the ``true``/``false`` string vmcli expects."""
    return "true" if v else "false"


# ---------------------------------------------------------------------------
# VM
# ---------------------------------------------------------------------------


class _VMModule:
    def __init__(self, run):
        self._run = run

    def create(self, name, dirpath, guest_type=None, custom_guest_type=None):
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
        return self._run("VM", "Create", vm_path=None, args=args)


# ---------------------------------------------------------------------------
# Chipset
# ---------------------------------------------------------------------------


class _ChipsetModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query chipset state (vCPU count, memory, etc.)."""
        return self._run("Chipset", "query", vm_path=vm_path)

    def set_vcpu_count(self, vcpus, vm_path=None):
        """
        Set the number of virtual CPUs.

        :param vcpus: Number of vCPUs
        :param vm_path: Path to the VMX file (falls back to instance vm_path)
        """
        return self._run("Chipset", "SetVCpuCount", vm_path=vm_path, args=[str(vcpus)])

    def set_mem_size(self, size_mb, vm_path=None):
        """
        Set memory size in MB.

        :param size_mb: Memory in megabytes
        :param vm_path: Path to the VMX file
        """
        return self._run("Chipset", "SetMemSize", vm_path=vm_path, args=[str(size_mb)])

    def set_cores_per_socket(self, cores, vm_path=None):
        """
        Set cores per socket.

        :param cores: Number of cores per socket
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Chipset", "SetCoresPerSocket", vm_path=vm_path, args=[str(cores)]
        )

    def set_simultaneous_threads(self, threads, vm_path=None):
        """
        Set simultaneous threads (SMT/hyperthreading) per vCPU.

        :param threads: Number of threads per vCPU
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Chipset", "SetSimultaneousThreads", vm_path=vm_path, args=[str(threads)]
        )


# ---------------------------------------------------------------------------
# Disk
# ---------------------------------------------------------------------------


class _DiskModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query the disk configuration of the VM."""
        return self._run("Disk", "query", vm_path=vm_path)

    def create(self, filepath, adapter, size, disk_type, vm_path=None):
        """
        Create a virtual disk file.

        :param filepath: Full path for the new ``.vmdk`` file
        :param adapter: Adapter type: ``ide``, ``buslogic``, or ``lsilogic``
        :param size: Capacity string, e.g. ``20GB`` or ``10240MB``
        :param disk_type: 0=single growable, 1=growable split, 2=preallocated, 3=preallocated split
        :param vm_path: Path to the VMX file
        """
        args = ["-f", filepath, "-a", adapter, "-s", size, "-t", str(disk_type)]
        return self._run("Disk", "Create", vm_path=vm_path, args=args)

    def extend(self, disk_label, new_num_sectors, vm_path=None):
        """
        Extend a virtual disk.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param new_num_sectors: Desired size in sectors
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Disk", "Extend", vm_path=vm_path, args=[disk_label, str(new_num_sectors)]
        )

    def move(self, from_label, to_label, vm_path=None):
        """
        Move a disk from one slot to another.

        :param from_label: Source device label, e.g. ``scsi0:0``
        :param to_label: Destination device label
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Disk", "Move", vm_path=vm_path, args=[from_label, to_label]
        )

    def branch(self, disk_label, vm_path=None):
        """
        Create a disk branch based on the current VM state.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param vm_path: Path to the VMX file
        """
        return self._run("Disk", "Branch", vm_path=vm_path, args=[disk_label])

    def connection_control(self, disk_label, connected, vm_path=None):
        """
        Connect or disconnect a disk device.

        :param disk_label: Device label, e.g. ``scsi0:0``
        :param connected: ``True`` to connect, ``False`` to disconnect
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Disk", "ConnectionControl", vm_path=vm_path, args=[disk_label, _b(connected)]
        )


# ---------------------------------------------------------------------------
# Ethernet
# ---------------------------------------------------------------------------


class _EthernetModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query ethernet adapter configuration."""
        return self._run("Ethernet", "query", vm_path=vm_path)

    def set_connection_type(self, device_label, connection_type, vm_path=None):
        """
        Set the connection type for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param connection_type: Connection type string (e.g. ``bridged``, ``nat``, ``hostonly``)
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Ethernet",
            "SetConnectionType",
            vm_path=vm_path,
            args=[device_label, connection_type],
        )

    def set_security_policy(
        self,
        device_label,
        no_promisc,
        down_when_addr_mismatch,
        no_forged_src_addr,
        vm_path=None,
    ):
        """
        Set the security policy for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param no_promisc: Disable promiscuous mode (bool)
        :param down_when_addr_mismatch: Bring link down on address mismatch (bool)
        :param no_forged_src_addr: Disallow forged source addresses (bool)
        :param vm_path: Path to the VMX file
        """
        args = [
            device_label,
            _b(no_promisc),
            _b(down_when_addr_mismatch),
            _b(no_forged_src_addr),
        ]
        return self._run("Ethernet", "SetSecurityPolicy", vm_path=vm_path, args=args)

    def set_network_name(self, device_label, network_name, vm_path=None):
        """
        Set the network name for an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param network_name: Name of the host network
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Ethernet",
            "SetNetworkName",
            vm_path=vm_path,
            args=[device_label, network_name],
        )

    def connection_control(self, device_label, connected, vm_path=None):
        """
        Connect or disconnect an ethernet adapter.

        :param device_label: Adapter label, e.g. ``ethernet0``
        :param connected: ``True`` to connect, ``False`` to disconnect
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Ethernet",
            "ConnectionControl",
            vm_path=vm_path,
            args=[device_label, _b(connected)],
        )


# ---------------------------------------------------------------------------
# MKS (display / keyboard / screen)
# ---------------------------------------------------------------------------


class _MKSModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query MKS (display and keyboard) state."""
        return self._run("MKS", "query", vm_path=vm_path)

    def capture_screenshot(self, filename, vm_path=None):
        """
        Capture a screenshot of the guest display.

        :param filename: Output file path on the host
        :param vm_path: Path to the VMX file
        """
        return self._run("MKS", "captureScreenshot", vm_path=vm_path, args=[filename])

    def send_key_event(self, hidcode, modifier, vm_path=None):
        """
        Send a single key event to the guest.

        :param hidcode: HID usage code for the key
        :param modifier: Modifier flags (e.g. 0 for none)
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "MKS", "sendKeyEvent", vm_path=vm_path, args=[str(hidcode), str(modifier)]
        )

    def send_key_sequence(self, sequence, vm_path=None):
        """
        Send a key sequence to the guest.

        :param sequence: Key sequence string
        :param vm_path: Path to the VMX file
        """
        return self._run("MKS", "sendKeySequence", vm_path=vm_path, args=[sequence])

    def set_guest_resolution(self, width, height, vm_path=None):
        """
        Set the guest display resolution.

        :param width: Width in pixels
        :param height: Height in pixels
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "MKS",
            "SetGuestResolution",
            vm_path=vm_path,
            args=[str(width), str(height)],
        )

    def set_num_displays(self, count, vm_path=None):
        """
        Set the number of displays in the VM.

        :param count: Number of displays
        :param vm_path: Path to the VMX file
        """
        return self._run("MKS", "SetNumDisplays", vm_path=vm_path, args=[str(count)])

    def set_3d_accel(self, enabled, vm_path=None):
        """
        Enable or disable 3D acceleration.

        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run("MKS", "SetAccel3d", vm_path=vm_path, args=[_b(enabled)])

    def set_vram_size(self, size_mb, vm_path=None):
        """
        Set the VRAM size.

        :param size_mb: VRAM size in MB
        :param vm_path: Path to the VMX file
        """
        return self._run("MKS", "SetVramSize", vm_path=vm_path, args=[str(size_mb)])

    def set_graphics_memory(self, size_kb, vm_path=None):
        """
        Set graphics memory size in kilobytes.

        :param size_kb: Graphics memory in KB
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "MKS", "SetGraphicsMemoryKB", vm_path=vm_path, args=[str(size_kb)]
        )


# ---------------------------------------------------------------------------
# ConfigParams
# ---------------------------------------------------------------------------


class _ConfigParamsModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Read all VMX configuration parameters."""
        return self._run("ConfigParams", "query", vm_path=vm_path)

    def set_entry(self, name, value, vm_path=None):
        """
        Write an arbitrary VMX configuration entry.

        :param name: Config key name
        :param value: Config key value
        :param vm_path: Path to the VMX file
        """
        return self._run("ConfigParams", "SetEntry", vm_path=vm_path, args=[name, value])


# ---------------------------------------------------------------------------
# HGFS (shared folders)
# ---------------------------------------------------------------------------


class _HGFSModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query HGFS shared folder state."""
        return self._run("HGFS", "query", vm_path=vm_path)

    def set_enabled(self, share_label, enabled, vm_path=None):
        """
        Enable or disable a shared folder.

        :param share_label: Share label
        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetEnabled", vm_path=vm_path, args=[share_label, _b(enabled)]
        )

    def set_read_access(self, share_label, readable, vm_path=None):
        """
        Set read access for a shared folder.

        :param share_label: Share label
        :param readable: ``True`` to allow reads
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetReadAccess", vm_path=vm_path, args=[share_label, _b(readable)]
        )

    def set_write_access(self, share_label, writable, vm_path=None):
        """
        Set write access for a shared folder.

        :param share_label: Share label
        :param writable: ``True`` to allow writes
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetWriteAccess", vm_path=vm_path, args=[share_label, _b(writable)]
        )

    def set_follow_symlinks(self, share_label, follow, vm_path=None):
        """
        Configure whether symlinks are followed in a shared folder.

        :param share_label: Share label
        :param follow: ``True`` to follow symlinks
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS",
            "SetFollowSymlinks",
            vm_path=vm_path,
            args=[share_label, _b(follow)],
        )

    def set_host_path(self, share_label, host_path, vm_path=None):
        """
        Set the host-side path for a shared folder.

        :param share_label: Share label
        :param host_path: Absolute host path
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetHostPath", vm_path=vm_path, args=[share_label, host_path]
        )

    def set_guest_name(self, share_label, guest_name, vm_path=None):
        """
        Set the name by which the guest sees a shared folder.

        :param share_label: Share label
        :param guest_name: Name visible inside the guest
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetGuestName", vm_path=vm_path, args=[share_label, guest_name]
        )

    def set_present(self, share_label, present, vm_path=None):
        """
        Mark a shared folder as present or absent.

        :param share_label: Share label
        :param present: ``True`` to mark as present
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "HGFS", "SetPresent", vm_path=vm_path, args=[share_label, _b(present)]
        )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class _ToolsModule:
    def __init__(self, run):
        self._run = run

    def install(self, vm_path=None):
        """Mount the VMware Tools installer ISO in the guest."""
        return self._run("Tools", "Install", vm_path=vm_path)

    def upgrade(self, cmdline=None, backing_type=None, backing_path=None, vm_path=None):
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
        return self._run("Tools", "Upgrade", vm_path=vm_path, args=args or None)

    def query(self, vm_path=None):
        """Query VMware Tools installation state."""
        return self._run("Tools", "Query", vm_path=vm_path)


# ---------------------------------------------------------------------------
# VMTemplate
# ---------------------------------------------------------------------------


class _VMTemplateModule:
    def __init__(self, run):
        self._run = run

    def create(self, template_path, name, source_vmx=None):
        """
        Create a VM template from a VMX file.

        :param template_path: Destination ``.vmtx`` file path
        :param name: Template display name
        :param source_vmx: Source VMX file (can also be set via vm_path)
        """
        args = ["-p", template_path, "-n", name]
        return self._run("VMTemplate", "Create", vm_path=source_vmx, args=args)

    def deploy(self, template_path):
        """
        Deploy a VM from a template.

        :param template_path: Path to the ``.vmtx`` template file
        """
        args = ["-p", template_path]
        return self._run("VMTemplate", "Deploy", vm_path=None, args=args)


# ---------------------------------------------------------------------------
# VProbes
# ---------------------------------------------------------------------------


class _VProbesModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query VProbes state."""
        return self._run("VProbes", "Query", vm_path=vm_path)

    def load(self, script, vm_path=None):
        """
        Load a VProbes script onto the VM.

        :param script: Path to the VProbes script file
        :param vm_path: Path to the VMX file
        """
        return self._run("VProbes", "Load", vm_path=vm_path, args=[script])

    def reset(self, vm_path=None):
        """Disable all active VProbes on the VM."""
        return self._run("VProbes", "Reset", vm_path=vm_path)

    def set_enabled(self, enabled, vm_path=None):
        """
        Enable or disable VProbes on the VM.

        :param enabled: ``True`` to enable VProbes
        :param vm_path: Path to the VMX file
        """
        return self._run("VProbes", "SetEnabled", vm_path=vm_path, args=[_b(enabled)])


# ---------------------------------------------------------------------------
# Guest (guest ops via VMware Tools)
# ---------------------------------------------------------------------------


class _GuestModule:
    def __init__(self, run, guest_args):
        self._run = run
        self._guest_args = guest_args

    def query(self, vm_path=None):
        """Query guest state."""
        return self._run("Guest", "query", vm_path=vm_path)

    def ls(self, path, vm_path=None):
        """
        List directory contents in the guest.

        :param path: Guest path to list
        :param vm_path: Path to the VMX file
        """
        return self._run("Guest", "ls", vm_path=vm_path, args=self._guest_args([path]))

    def mkdir(self, path, vm_path=None):
        """
        Create a directory in the guest.

        :param path: Guest path to create
        :param vm_path: Path to the VMX file
        """
        return self._run("Guest", "mkdir", vm_path=vm_path, args=self._guest_args([path]))

    def rm(self, path, vm_path=None):
        """
        Remove a file in the guest.

        :param path: Guest file path to remove
        :param vm_path: Path to the VMX file
        """
        return self._run("Guest", "rm", vm_path=vm_path, args=self._guest_args([path]))

    def rmdir(self, path, vm_path=None):
        """
        Remove a directory in the guest.

        :param path: Guest directory path to remove
        :param vm_path: Path to the VMX file
        """
        return self._run("Guest", "rmdir", vm_path=vm_path, args=self._guest_args([path]))

    def mv(self, src, dst, vm_path=None):
        """
        Move/rename a file in the guest.

        :param src: Source guest path
        :param dst: Destination guest path
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Guest", "mv", vm_path=vm_path, args=self._guest_args([src, dst])
        )

    def mvdir(self, src, dst, vm_path=None):
        """
        Move a directory in the guest.

        :param src: Source guest path
        :param dst: Destination guest path
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Guest", "mvdir", vm_path=vm_path, args=self._guest_args([src, dst])
        )

    def ps(self, pid=None, vm_path=None):
        """
        List running processes in the guest.

        :param pid: Filter by PID (optional)
        :param vm_path: Path to the VMX file
        """
        extra = []
        if pid is not None:
            extra.extend(["-pid", str(pid)])
        return self._run("Guest", "ps", vm_path=vm_path, args=self._guest_args(extra))

    def kill(self, pid, vm_path=None):
        """
        Kill a process in the guest.

        :param pid: PID to kill
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Guest", "kill", vm_path=vm_path, args=self._guest_args([str(pid)])
        )

    def run(
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
        return self._run("Guest", "run", vm_path=vm_path, args=self._guest_args(extra))

    def copy_from(self, guest_path, host_path, vm_path=None):
        """
        Copy a file from the guest to the host.

        :param guest_path: Source path inside the guest
        :param host_path: Destination path on the host
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Guest",
            "copyFrom",
            vm_path=vm_path,
            args=self._guest_args([guest_path, host_path]),
        )

    def copy_to(self, host_path, guest_path, vm_path=None):
        """
        Copy a file from the host to the guest.

        :param host_path: Source path on the host
        :param guest_path: Destination path inside the guest
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Guest",
            "copyTo",
            vm_path=vm_path,
            args=self._guest_args([host_path, guest_path]),
        )

    def create_temp_dir(self, vm_path=None):
        """Create a temporary directory in the guest."""
        return self._run(
            "Guest", "createTempDir", vm_path=vm_path, args=self._guest_args()
        )

    def create_temp_file(self, vm_path=None):
        """Create a temporary file in the guest."""
        return self._run(
            "Guest", "createTempFile", vm_path=vm_path, args=self._guest_args()
        )

    def env(self, vm_path=None):
        """List environment variables in the guest."""
        return self._run("Guest", "env", vm_path=vm_path, args=self._guest_args())


# ---------------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------------


class _PowerModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query the current power state of the VM."""
        return self._run("Power", "query", vm_path=vm_path)

    def start(self, vm_path=None):
        """Start the VM."""
        return self._run("Power", "Start", vm_path=vm_path)

    def stop(self, vm_path=None):
        """Stop the VM."""
        return self._run("Power", "Stop", vm_path=vm_path)

    def pause(self, vm_path=None):
        """Pause the VM."""
        return self._run("Power", "Pause", vm_path=vm_path)

    def reset(self, vm_path=None):
        """Reset the VM."""
        return self._run("Power", "Reset", vm_path=vm_path)

    def suspend(self, vm_path=None):
        """Suspend the VM."""
        return self._run("Power", "Suspend", vm_path=vm_path)

    def unpause(self, vm_path=None):
        """Unpause the VM."""
        return self._run("Power", "Unpause", vm_path=vm_path)


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------


class _SnapshotModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query snapshot configuration."""
        return self._run("Snapshot", "query", vm_path=vm_path)

    def take(self, name, vm_path=None):
        """
        Take a snapshot of the VM.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run("Snapshot", "Take", vm_path=vm_path, args=[name])

    def delete(self, name, vm_path=None):
        """
        Delete a snapshot from the VM.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run("Snapshot", "Delete", vm_path=vm_path, args=[name])

    def revert(self, name, vm_path=None):
        """
        Revert the VM to a snapshot.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run("Snapshot", "Revert", vm_path=vm_path, args=[name])

    def clone(self, name, vm_path=None):
        """
        Clone from a snapshot.

        :param name: Snapshot name
        :param vm_path: Path to the VMX file
        """
        return self._run("Snapshot", "Clone", vm_path=vm_path, args=[name])


# ---------------------------------------------------------------------------
# Shared HBA base (Nvme + Sata)
# ---------------------------------------------------------------------------


class _HBAModule:
    """Shared commands common to both Nvme and Sata HBA modules."""

    def __init__(self, run, module):
        self._run = run
        self._mod = module

    def query(self, vm_path=None):
        """Query the state of the HBA."""
        return self._run(self._mod, "query", vm_path=vm_path)

    def purge(self, device_label, vm_path=None):
        """
        Remove the given HBA and clean out the configuration.

        :param device_label: Device label, e.g. ``nvme0`` or ``sata0``
        :param vm_path: Path to the VMX file
        """
        return self._run(self._mod, "Purge", vm_path=vm_path, args=[device_label])

    def move(self, from_label, to_label, vm_path=None):
        """
        Move a device from one slot to another.

        :param from_label: Source device label
        :param to_label: Destination device label
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod, "Move", vm_path=vm_path, args=[from_label, to_label]
        )

    def set_present(self, device_label, enabled, vm_path=None):
        """
        Enable or disable the given device.

        :param device_label: Device label
        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod, "SetPresent", vm_path=vm_path, args=[device_label, _b(enabled)]
        )

    def set_type(self, device_label, hba_type, vm_path=None):
        """
        Set the HBA type attribute.

        :param device_label: Device label
        :param hba_type: HBA type string
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod, "SetType", vm_path=vm_path, args=[device_label, hba_type]
        )

    def set_pci_slot_number(self, device_label, pci_slot_number, vm_path=None):
        """
        Set the PCI slot number of the specified device.

        :param device_label: Device label
        :param pci_slot_number: PCI slot number
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod,
            "SetPciSlotNumber",
            vm_path=vm_path,
            args=[device_label, str(pci_slot_number)],
        )

    def set_max_devices(self, device_label, max_devices, vm_path=None):
        """
        Set the maximum number of devices per HBA.

        :param device_label: Device label
        :param max_devices: Maximum number of devices
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod,
            "SetMaxDevices",
            vm_path=vm_path,
            args=[device_label, str(max_devices)],
        )

    def is_child_present(self, device_label, vm_path=None):
        """
        Determine if the specified child device is present.

        :param device_label: Device label
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod, "IsChildPresent", vm_path=vm_path, args=[device_label]
        )

    def find_first_free(self, device_label, vm_path=None):
        """
        Find the first available device address.

        :param device_label: Device label
        :param vm_path: Path to the VMX file
        """
        return self._run(
            self._mod, "FindFirstFree", vm_path=vm_path, args=[device_label]
        )


# ---------------------------------------------------------------------------
# Nvme  (extends _HBAModule)
# ---------------------------------------------------------------------------


class _NvmeModule(_HBAModule):
    def __init__(self, run):
        super().__init__(run, "Nvme")

    def set_bus_type(self, device_label, bus_type, vm_path=None):
        """
        Set the bus type attribute of a NVMe HBA.

        :param device_label: Device label
        :param bus_type: Bus type string
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Nvme", "SetBusType", vm_path=vm_path, args=[device_label, bus_type]
        )


# ---------------------------------------------------------------------------
# Sata  (extends _HBAModule)
# ---------------------------------------------------------------------------


class _SataModule(_HBAModule):
    def __init__(self, run):
        super().__init__(run, "Sata")

    def is_present(self, device_label, vm_path=None):
        """
        Determine if the specified SATA device is present.

        :param device_label: Device label
        :param vm_path: Path to the VMX file
        """
        return self._run("Sata", "IsPresent", vm_path=vm_path, args=[device_label])

    def has_no_device(self, device_label, vm_path=None):
        """
        Determine if the SATA controller has no device attached.

        :param device_label: Device label
        :param vm_path: Path to the VMX file
        """
        return self._run("Sata", "HasNoDevice", vm_path=vm_path, args=[device_label])

    def set_numa_node(self, device_label, numa_node, vm_path=None):
        """
        Set the NUMA node attribute of the specified SATA device.

        :param device_label: Device label
        :param numa_node: NUMA node number
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Sata",
            "SetNumaNode",
            vm_path=vm_path,
            args=[device_label, str(numa_node)],
        )


# ---------------------------------------------------------------------------
# Serial
# ---------------------------------------------------------------------------


class _SerialModule:
    def __init__(self, run):
        self._run = run

    def query(self, vm_path=None):
        """Query the state of the serial ports."""
        return self._run("Serial", "Query", vm_path=vm_path)

    def purge(self, device_label, vm_path=None):
        """
        Remove the given serial device and clean out the configuration.

        :param device_label: Device label, e.g. ``serial0``
        :param vm_path: Path to the VMX file
        """
        return self._run("Serial", "Purge", vm_path=vm_path, args=[device_label])

    def connection_control(self, device_label, op_type, vm_path=None):
        """
        Modify the connection state of the specified serial device.

        :param device_label: Device label
        :param op_type: Operation type string
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "ConnectionControl",
            vm_path=vm_path,
            args=[device_label, op_type],
        )

    def set_allow_guest_control(self, device_label, allow, vm_path=None):
        """
        Update the allowGuestControl state for a serial port.

        :param device_label: Device label
        :param allow: ``True`` to allow guest control, ``False`` to disallow
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "SetAllowGuestControl",
            vm_path=vm_path,
            args=[device_label, _b(allow)],
        )

    def set_backing_info(
        self,
        device_label,
        backing_type,
        backing_path,
        backing_path_net_proxy,
        pipe_end_point,
        net_end_point,
        vm_path=None,
    ):
        """
        Set up the backing for the given serial port.

        :param device_label: Device label
        :param backing_type: Backing type
        :param backing_path: Backing path
        :param backing_path_net_proxy: Backing net proxy path
        :param pipe_end_point: Pipe end point
        :param net_end_point: Net end point
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "SetBackingInfo",
            vm_path=vm_path,
            args=[
                device_label,
                backing_type,
                backing_path,
                backing_path_net_proxy,
                pipe_end_point,
                net_end_point,
            ],
        )

    def set_present(self, device_label, enabled, vm_path=None):
        """
        Enable or disable the given serial device.

        :param device_label: Device label
        :param enabled: ``True`` to enable, ``False`` to disable
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial", "SetPresent", vm_path=vm_path, args=[device_label, _b(enabled)]
        )

    def start_connected(self, device_label, start_connected, vm_path=None):
        """
        Update the startConnected state for a serial port (takes effect on next power-on).

        :param device_label: Device label
        :param start_connected: ``True`` to start connected, ``False`` otherwise
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "StartConnected",
            vm_path=vm_path,
            args=[device_label, _b(start_connected)],
        )

    def try_no_rx_loss(self, device_label, try_no_rx_loss, vm_path=None):
        """
        Control the VM's ability to buffer serial receive data.

        :param device_label: Device label
        :param try_no_rx_loss: ``True`` to enable no-rx-loss buffering
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "TryNoRxLoss",
            vm_path=vm_path,
            args=[device_label, _b(try_no_rx_loss)],
        )

    def yield_on_msr_read(self, device_label, yield_on_msr_read, vm_path=None):
        """
        Control whether the VM yields processor time when polling the serial port.

        :param device_label: Device label
        :param yield_on_msr_read: ``True`` to yield on MSR read
        :param vm_path: Path to the VMX file
        """
        return self._run(
            "Serial",
            "YieldOnMsrRead",
            vm_path=vm_path,
            args=[device_label, _b(yield_on_msr_read)],
        )


# ---------------------------------------------------------------------------
# VMwareCLI  (top-level public class)
# ---------------------------------------------------------------------------


class VMwareCLI:
    """
    Wrapper for the vmcli CLI that ships alongside VMware Fusion.

    vmcli exposes functionality not available through vmrun, including VM
    creation, chipset configuration, disk management, ethernet setup,
    display/keyboard control (MKS), guest operations, shared folder
    fine-tuning (HGFS), VMware Tools upgrade, VM templates, VProbes, and
    arbitrary VMX config-param access.

    Commands are grouped by vmcli module and accessed as sub-objects::

        import shutil
        from vmware_fusion_py import VMwareCLI

        vmcli = VMwareCLI(
            vmcli_path=shutil.which("vmcli"),
            vm_path="/path/to/vm.vmx",
            guest_user="user",
            guest_password="pass",
        )
        vmcli.chipset.set_vcpu_count(4)
        vmcli.chipset.set_mem_size(8192)
        vmcli.snapshot.take("before-update")
        vmcli.nvme.purge("nvme0")
        vmcli.sata.set_present("sata0", True)
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

        self.vm = _VMModule(self._run_command)
        self.chipset = _ChipsetModule(self._run_command)
        self.disk = _DiskModule(self._run_command)
        self.ethernet = _EthernetModule(self._run_command)
        self.mks = _MKSModule(self._run_command)
        self.config = _ConfigParamsModule(self._run_command)
        self.hgfs = _HGFSModule(self._run_command)
        self.tools = _ToolsModule(self._run_command)
        self.template = _VMTemplateModule(self._run_command)
        self.vprobes = _VProbesModule(self._run_command)
        self.guest = _GuestModule(self._run_command, self._guest_args)
        self.power = _PowerModule(self._run_command)
        self.snapshot = _SnapshotModule(self._run_command)
        self.nvme = _NvmeModule(self._run_command)
        self.sata = _SataModule(self._run_command)
        self.serial = _SerialModule(self._run_command)

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

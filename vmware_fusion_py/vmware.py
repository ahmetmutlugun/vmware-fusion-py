import subprocess


def _provide_vm_path(func):
    def wrapper(self, *args, **kwargs):
        if "vm_path" in kwargs.keys():
            return func(self, *args, **kwargs)

        if self.vm_path is not None:
            return func(self, vm_path=self.vm_path, *args, **kwargs)

        return func(self, *args, **kwargs)

    return wrapper


class VMware:
    def __init__(
        self,
        vmrun_path: str,
        host_type: str = "",
        vm_password: str = "",
        guest_user: str = "",
        guest_password: str = "",
        vm_path: str = "",
    ) -> None:

        self.vmrun_path = vmrun_path
        self.host_type = host_type
        self.vm_password = vm_password
        self.guest_user = guest_user
        self.guest_password = guest_password
        self.vm_path = vm_path

    def set_vmrun_path(self, vmrun_path):
        self.vmrun_path = vmrun_path

    def set_host_type(self, host_type):
        self.host_type = host_type

    def set_vm_password(self, vm_password):
        self.vm_password = vm_password

    def set_guest_user(self, guest_user):
        self.guest_user = guest_user

    def set_guest_password(self, guest_password):
        self.guest_password = guest_password

    def set_vm_path(self, vm_path):
        self.vm_path = vm_path

    def _run_command(self, command, vm_path, options=None):
        cmd = [self.vmrun_path]

        if vm_path:
            proc = subprocess.Popen([self.vmrun_path, command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode("utf-8").strip()
            stderr = stderr.decode("utf-8").strip()
            return {"return_code": proc.returncode, "output": stdout}


        if self.host_type:
            cmd.extend(["-T", self.host_type])
        if self.vm_password:
            cmd.extend(["-vp", self.vm_password])
        if self.guest_user:
            cmd.extend(["-gu", self.guest_user])
        if self.guest_password:
            cmd.extend(["-gp", self.guest_password])
        cmd.append(command)
        cmd.append(vm_path)
        if options:
            cmd.extend(options)
        try:
            print(cmd)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode("utf-8").strip()
            stderr = stderr.decode("utf-8").strip()
            return {"return_code": proc.returncode, "output": stdout}
        except FileNotFoundError as e:
            return {"return_code": 2, "output": "File not found!"}

    @_provide_vm_path
    def start(self, vm_path=None, nogui=False):
        options = ["nogui"] if nogui else ["gui"]
        return self._run_command("start", vm_path, options)

    @_provide_vm_path
    def stop(self, vm_path=None, hard=False):
        options = ["hard"] if hard else ["soft"]
        return self._run_command("stop", vm_path, options)

    @_provide_vm_path
    def reset(self, vm_path=None, hard=False):
        options = ["hard"] if hard else ["soft"]
        return self._run_command("reset", vm_path, options)

    @_provide_vm_path
    def suspend(self, vm_path=None, hard=False):
        options = ["hard"] if hard else ["soft"]
        return self._run_command("suspend", vm_path, options)

    @_provide_vm_path
    def pause(self, vm_path=None):
        return self._run_command("pause", vm_path)

    @_provide_vm_path
    def unpause(self, vm_path=None):
        return self._run_command("unpause", vm_path)

    @_provide_vm_path
    def list_snapshots(self, vm_path=None, show_tree=False):
        options = ["showTree"] if show_tree else []
        return self._run_command("listSnapshots", vm_path, options)

    @_provide_vm_path
    def snapshot(self, snapshot_name, vm_path=None):
        options = [snapshot_name]
        return self._run_command("snapshot", vm_path, options)

    @_provide_vm_path
    def delete_snapshot(self, snapshot_name, vm_path=None, and_delete_children=False):
        options = [snapshot_name]
        if and_delete_children:
            options.append("andDeleteChildren")
        return self._run_command("deleteSnapshot", vm_path, options)

    @_provide_vm_path
    def revert_to_snapshot(self, snapshot_name, vm_path=None):
        options = [snapshot_name]
        return self._run_command("revertToSnapshot", vm_path, options)

    @_provide_vm_path
    def list_network_adapters(self, vm_path):
        return self._run_command("listNetworkAdapters", vm_path)

    @_provide_vm_path
    def add_network_adapter(self, adapter_type, host_network=None, vm_path=None):
        options = [adapter_type]
        if host_network:
            options.append(host_network)
        return self._run_command("addNetworkAdapter", vm_path, options)

    @_provide_vm_path
    def set_network_adapter(
        self, adapter_index, adapter_type, host_network=None, vm_path=None
    ):
        options = [str(adapter_index), adapter_type]
        if host_network:
            options.append(host_network)
        return self._run_command("setNetworkAdapter", vm_path, options)

    @_provide_vm_path
    def delete_network_adapter(self, adapter_index, vm_path=None):
        options = [str(adapter_index)]
        return self._run_command("deleteNetworkAdapter", vm_path, options)

    def list_host_networks(self):
        return self._run_command("listHostNetworks", None)

    def list_port_forwardings(self, host_network_name):
        return self._run_command("listPortForwardings", host_network_name)

    def set_port_forwarding(
        self,
        host_network_name,
        protocol,
        host_port,
        guest_ip,
        guest_port,
        description=None,
    ):
        options = [protocol, str(host_port), guest_ip, str(guest_port)]
        if description:
            options.append(description)
        return self._run_command("setPortForwarding", host_network_name, options)

    def delete_port_forwarding(self, host_network_name, protocol, host_port):
        options = [protocol, str(host_port)]
        return self._run_command("deletePortForwarding", host_network_name, options)

    @_provide_vm_path
    def run_program_in_guest(
        self,
        program_path,
        no_wait=False,
        active_window=False,
        interactive=False,
        program_arguments=None,
        vm_path=None,
    ):
        options = []
        if no_wait:
            options.append("-noWait")
        if active_window:
            options.append("-activeWindow")
        if interactive:
            options.append("-interactive")
        options.append(program_path)
        if program_arguments:
            options.extend(program_arguments)
        return self._run_command("runProgramInGuest", vm_path, options)

    @_provide_vm_path
    def file_exists_in_guest(self, file_path, vm_path=None):
        options = [file_path]
        return self._run_command("fileExistsInGuest", vm_path, options)

    @_provide_vm_path
    def directory_exists_in_guest(self, directory_path, vm_path=None):
        options = [directory_path]
        return self._run_command("directoryExistsInGuest", vm_path, options)

    @_provide_vm_path
    def set_shared_folder_state(self, share_name, host_path, mode, vm_path=None):
        options = [share_name, host_path, mode]
        return self._run_command("setSharedFolderState", vm_path, options)

    @_provide_vm_path
    def add_shared_folder(self, share_name, host_path, vm_path=None):
        options = [share_name, host_path]
        return self._run_command("addSharedFolder", vm_path, options)

    @_provide_vm_path
    def remove_shared_folder(self, share_name, vm_path=None):
        options = [share_name]
        return self._run_command("removeSharedFolder", vm_path, options)

    @_provide_vm_path
    def enable_shared_folders(self, runtime=False, vm_path=None):
        options = ["runtime"] if runtime else []
        return self._run_command("enableSharedFolders", vm_path, options)

    @_provide_vm_path
    def disable_shared_folders(self, runtime=False, vm_path=None):
        options = ["runtime"] if runtime else []
        return self._run_command("disableSharedFolders", vm_path, options)

    @_provide_vm_path
    def list_processes_in_guest(self, vm_path=None):
        return self._run_command("listProcessesInGuest", vm_path)

    @_provide_vm_path
    def kill_process_in_guest(self, process_id, vm_path=None):
        options = [str(process_id)]
        return self._run_command("killProcessInGuest", vm_path, options)

    @_provide_vm_path
    def run_script_in_guest(
        self,
        interpreter_path,
        script_text,
        no_wait=False,
        active_window=False,
        interactive=False,
        vm_path=None
    ):
        options = []
        if no_wait:
            options.append("-noWait")
        if active_window:
            options.append("-activeWindow")
        if interactive:
            options.append("-interactive")
        options.extend([interpreter_path, script_text])
        return self._run_command("runScriptInGuest", vm_path, options)

    @_provide_vm_path
    def delete_file_in_guest(self, file_path, vm_path=None):
        options = [file_path]
        return self._run_command("deleteFileInGuest", vm_path, options)

    @_provide_vm_path
    def create_directory_in_guest(self, directory_path, vm_path=None):
        options = [directory_path]
        return self._run_command("createDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def delete_directory_in_guest(self, directory_path, vm_path=None):
        options = [directory_path]
        return self._run_command("deleteDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def create_temp_file_in_guest(self, vm_path=None):
        return self._run_command("createTempfileInGuest", vm_path)

    @_provide_vm_path
    def list_directory_in_guest(self, directory_path, vm_path=None):
        options = [directory_path]
        return self._run_command("listDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def copy_file_from_host_to_guest(self, host_path, guest_path, vm_path=None):
        options = [host_path, guest_path]
        return self._run_command("CopyFileFromHostToGuest", vm_path, options)

    @_provide_vm_path
    def copy_file_from_guest_to_host(self, guest_path, host_path, vm_path=None):
        options = [guest_path, host_path]
        return self._run_command("CopyFileFromGuestToHost", vm_path, options)

    @_provide_vm_path
    def rename_file_in_guest(self, original_name, new_name, vm_path=None):
        options = [original_name, new_name]
        return self._run_command("renameFileInGuest", vm_path, options)

    @_provide_vm_path
    def type_keystrokes_in_guest(self, keystroke_string, vm_path=None):
        options = [keystroke_string]
        return self._run_command("typeKeystrokesInGuest", vm_path, options)

    @_provide_vm_path
    def connect_named_device(self, device_name, vm_path=None):
        options = [device_name]
        return self._run_command("connectNamedDevice", vm_path, options)

    @_provide_vm_path
    def disconnect_named_device(self, vm_path, device_name):
        options = [device_name]
        return self._run_command("disconnectNamedDevice", vm_path, options)

    @_provide_vm_path
    def capture_screen(self, host_path, vm_path=None):
        options = [host_path]
        return self._run_command("captureScreen", vm_path, options)

    @_provide_vm_path
    def write_variable(self, variable_type, variable_name, variable_value, vm_path=None):
        options = [variable_type, variable_name, variable_value]
        return self._run_command("writeVariable", vm_path, options)

    @_provide_vm_path
    def read_variable(self, variable_type, variable_name, vm_path=None):
        options = [variable_type, variable_name]
        return self._run_command("readVariable", vm_path, options)

    @_provide_vm_path
    def get_guest_ip_address(self, wait=False, vm_path=None):
        options = ["-wait"] if wait else []
        return self._run_command("getGuestIPAddress", vm_path, options)

    def list(self):
        return self._run_command("list", None)

    @_provide_vm_path
    def upgrade_vm(self, vm_path=None):
        return self._run_command("upgradevm", vm_path)

    @_provide_vm_path
    def install_tools(self, vm_path=None):
        return self._run_command("installTools", vm_path)

    @_provide_vm_path
    def check_tools_state(self, vm_path=None):
        return self._run_command("checkToolsState", vm_path)

    @_provide_vm_path
    def delete_vm(self, vm_path=None):
        return self._run_command("deleteVM", vm_path)

    @_provide_vm_path
    def clone(
        self, destination_path, clone_type, snapshot=None, clone_name=None, vm_path=None
    ):
        options = [destination_path, clone_type]
        if snapshot:
            options.extend(["-snapshot", snapshot])
        if clone_name:
            options.extend(["-cloneName", clone_name])
        return self._run_command("clone", vm_path, options)

    def download_photon_vm(self, destination_path):
        return self._run_command("downloadPhotonVM", destination_path)

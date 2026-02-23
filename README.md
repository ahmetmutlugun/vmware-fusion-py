![PyPI - Version](https://img.shields.io/pypi/v/vmware-fusion-py)
![GitHub License](https://img.shields.io/github/license/ahmetmutlugun/vmware-fusion-py)

# vmware-fusion-py

A Python wrapper for controlling VMware Fusion virtual machines through the `vmrun` and `vmcli` command-line utilities. Designed for automation, scripting, and programmatic VM management on macOS.

## Features

**`VMware` — full `vmrun` coverage**
- Power control: start, stop, reset, suspend, pause, unpause
- Snapshot management: create, delete, list, revert
- Network adapters: list, add, configure, delete
- Port forwarding: create, delete, list
- Guest execution: run programs and scripts, manage processes
- Guest filesystem: copy files, create/delete files and directories, rename, list
- Shared folders: add, remove, enable, disable, set state
- Guest interaction: type keystrokes, capture screenshots, read/write variables
- VM lifecycle: clone, delete, upgrade, install/check VMware Tools

**`VMwareCLI` — full `vmcli` coverage**
- Create new VMs with configurable guest OS type
- Chipset: set vCPU count, memory size, cores per socket, simultaneous threads
- Disk: create, extend, move, branch disks; connection control
- Ethernet: query adapters, set connection type, network name, security policy
- MKS: set guest resolution, display count, 3D acceleration, VRAM, graphics memory; send key events and sequences; capture screenshots
- ConfigParams: read and write arbitrary VMX configuration entries
- HGFS: fine-grained shared folder control — enable/disable, read/write access, symlink following, host path, guest name
- Tools: install, upgrade, and query VMware Tools state
- VMTemplate: create and deploy VM templates
- VProbes: load, enable, reset VProbes scripts
- Guest ops: `ls`, `mkdir`, `rm`, `mv`, `ps`, `kill`, `run`, `copyFrom`, `copyTo`, `env`, create temp files and directories
- Power and snapshot control (native vmcli)

## Requirements

- Python 3.8+
- VMware Fusion on macOS
- `vmrun` and `vmcli` (included with VMware Fusion)

## Installation

```bash
pip install vmware-fusion-py
```

**From source:**

```bash
git clone https://github.com/ahmetmutlugun/vmware-fusion-py
cd vmware-fusion-py
pip install .
```

## Usage

### VMware (vmrun)

```python
import shutil
from vmware_fusion_py import VMware

vmrun_path = shutil.which("vmrun")
vm = VMware(
    vmrun_path=vmrun_path,
    host_type="fusion",
    guest_user="username",
    guest_password="password",
    vm_path="/path/to/vm.vmx",
)

# Power
vm.start()
vm.stop()

# Snapshots
vm.snapshot("before-update")
vm.revert_to_snapshot("before-update")

# Guest filesystem
vm.copy_file_from_host_to_guest("/host/file.txt", "/guest/file.txt")
vm.run_program_in_guest("/usr/bin/python3", program_arguments=["/guest/script.py"])

# Processes
result = vm.list_processes_in_guest()
processes = result["processes"]  # {pid: {"owner": ..., "cmd": ...}}
```

The `vm_path` can be set at construction time (as above) and is injected automatically into every call, or passed per-call as a keyword argument:

```python
vm = VMware(vmrun_path=vmrun_path)
vm.start(vm_path="/path/to/vm.vmx")
```

All methods return a dict with at minimum:

| Key | Description |
|-----|-------------|
| `return_code` | Process exit code (`0` = success) |
| `output` | stdout from vmrun |
| `error` | stderr from vmrun |

### VMwareCLI (vmcli)

```python
import shutil
from vmware_fusion_py import VMwareCLI

vmcli = VMwareCLI(
    vmcli_path=shutil.which("vmcli"),
    vm_path="/path/to/vm.vmx",
    guest_user="username",
    guest_password="password",
)

# Create a new VM
vmcli.create_vm(name="myVM", dirpath="~/VMs", guest_type="arm-ubuntu-64")

# Configure hardware
vmcli.set_vcpu_count(4)
vmcli.set_mem_size(8192)
vmcli.set_cores_per_socket(2)

# Display
vmcli.set_guest_resolution(1920, 1080)
vmcli.set_3d_accel(True)
vmcli.set_vram_size(256)

# VMX config
vmcli.set_config_entry("tools.syncTime", "TRUE")
cfg = vmcli.query_config()

# Disk
vmcli.create_disk("/path/disk.vmdk", adapter="lsilogic", size="50GB", disk_type=0)
vmcli.extend_disk("scsi0:0", new_num_sectors=104857600)

# Shared folders (fine-grained)
vmcli.set_share_enabled("myShare", True)
vmcli.set_share_write_access("myShare", True)
vmcli.set_share_follow_symlinks("myShare", False)

# Guest ops
vmcli.guest_ls("/home/user")
vmcli.guest_run("/usr/bin/python3", program_args=["/tmp/script.py"])
vmcli.guest_copy_to("/host/file.txt", "/guest/file.txt")

# Tools
vmcli.upgrade_tools()

# VM templates
vmcli.create_template("/path/template.vmtx", name="myTemplate")
vmcli.deploy_template("/path/template.vmtx")

# VProbes
vmcli.set_vprobes_enabled(True)
vmcli.load_vprobes("/path/script.vp")
```

## License

MIT License — see [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome.

## Author

[Ahmet Mutlugun](https://github.com/ahmetmutlugun)

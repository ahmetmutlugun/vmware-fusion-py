![PyPI - Version](https://img.shields.io/pypi/v/vmware-fusion-py)
![GitHub License](https://img.shields.io/github/license/ahmetmutlugun/vmware-fusion-py)

# vmware-fusion-py

This Python module provides a convenient way to control and interact with VMware Fusion virtual machines using the `vmrun` command-line utility. Built and tested for VMware Fusion on arm64 MacOS

## Features

- Full coverage of the `vmrun` CLI
  - Start, stop, reset, suspend, pause, and unpause virtual machines
  - Manage snapshots (create, delete, list, and revert)
  - Manage network adapters (list, add, set, and delete)
  - Manage port forwarding for host networks
  - Run programs and scripts in the guest operating system
  - Manage files and directories in the guest operating system
  - Manage shared folders between the host and guest
  - Interact with the guest operating system (type keystrokes, capture screenshots, etc.)
  - Clone virtual machines
  - Upgrade virtual machines and install VMware Tools

## Prerequisites

- Python 3.x
- VMware Fusion on MacOS
- `vmrun` command-line utility (included with VMware Fusion)

## Installation
### Pip
`pip install vmware-fusion-py`
### From Source
1. Clone the repository or download the source code.
2. Install the package using `pip install .`
## Usage
### Initialization
```python
# Get vmrun path or provide the path as a string
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    # vmrun is installed automatically alongside VMware Fusion. Install VMware
    exit()
# Initiate client
client = VMware(vmrun_path=vmrun_path)
```
### Presets
```python
client = VMware(
    vmrun_path="/path/to/vmrun",
    host_type="ws",
    vm_password="password",
    guest_user="username",
    guest_password="password",
    vm_path="/path/to/vm"
)
```
## License
This project is licensed under the MIT License.

## Contributors
- Ahmet Mutlugun [Github](https://github.com/ahmetmutlugun)

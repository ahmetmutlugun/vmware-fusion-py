import shutil
from vmware_fusion_py import VMware

# Initialize vmware class
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    print(
        "Could not find vmrun. Install VMware Fusion from https://www.vmware.com/products/desktop-hypervisor.html"
    )
    exit()


client = VMware(vmrun_path=vmrun_path)

print(client.list())

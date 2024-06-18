import shutil
from vmware_fusion_py import VMware

# Initialize vmware class
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    print(
        f"Could not find vmrun. Install vmrun from {"".format('', "https://www.vmware.com/products/desktop-hypervisor.html", "VMware")}"
    )
    exit()


client = VMware(vmrun_path=vmrun_path)

print(client.list())

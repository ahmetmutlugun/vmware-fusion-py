import os
import shutil

from vmware_fusion_py import VMRest, VMware
from vmware_fusion_py.vmrest import VMRestConnectionError

# Initialize vmware class
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    print(
        "Could not find vmrun. Install VMware Fusion from https://www.vmware.com/products/desktop-hypervisor.html"
    )
    exit()


client = VMware(vmrun_path=vmrun_path)

print(client.list())

# ---------------------------------------------------------------------------
# VMRest smoke test
# ---------------------------------------------------------------------------

vmrest_user = os.environ.get("VMREST_USER")
vmrest_pass = os.environ.get("VMREST_PASS")

if not vmrest_user or not vmrest_pass:
    print("Skipping VMRest smoke test: set VMREST_USER and VMREST_PASS to run it.")
else:
    rest = VMRest(username=vmrest_user, password=vmrest_pass)
    try:
        vms = rest.vms.list()
        print(f"VMRest vms.list(): {vms}")
        nets = rest.network.list_vmnets()
        print(f"VMRest network.list_vmnets(): {nets}")
    except VMRestConnectionError as exc:
        print(f"Skipping VMRest smoke test: vmrest not running ({exc})")

"""VMRest — Python wrapper for the vmrest local REST API (VMware Fusion Pro 13+).

Start vmrest before using this class:
    /Applications/VMware Fusion.app/Contents/Public/vmrest -C   # first-time credential setup
    /Applications/VMware Fusion.app/Contents/Public/vmrest       # start the server

Thread safety: requests.Session is not thread-safe. Create one VMRest instance per thread.
"""

from __future__ import annotations

from typing import Any, Callable

import requests


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class VMRestError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class VMRestConnectionError(VMRestError):
    """Network error or timeout reaching vmrest."""


class VMRestAuthError(VMRestError):
    """401 — bad credentials."""


class VMRestNotFoundError(VMRestError):
    """404 — resource not found."""


class VMRestInvalidParamError(VMRestError):
    """400 — invalid parameter."""


class VMRestConflictError(VMRestError):
    """409 — conflict (e.g. VM already exists)."""


class VMRestServerError(VMRestError):
    """5xx — server-side error."""


_STATUS_MAP: dict[int, type[VMRestError]] = {
    400: VMRestInvalidParamError,
    401: VMRestAuthError,
    404: VMRestNotFoundError,
    409: VMRestConflictError,
}

_Requester = Callable[..., Any]


# ---------------------------------------------------------------------------
# _VMsModule
# ---------------------------------------------------------------------------


class _VMsModule:
    """Methods under /api/vms — accessible as ``vmrest.vms.*``."""

    def __init__(self, request: _Requester) -> None:
        self._request = request

    def list(self) -> list[dict]:
        """GET /vms — list all registered VMs."""
        return self._request("GET", "/vms")

    def get(self, vm_id: str) -> dict:
        """GET /vms/{id} — get VM configuration."""
        return self._request("GET", f"/vms/{vm_id}")

    def update(self, vm_id: str, *, cpu: int, memory: int) -> dict:
        """PUT /vms/{id} — update CPU count and memory (MB)."""
        return self._request(
            "PUT",
            f"/vms/{vm_id}",
            json={"processors": cpu, "memory": memory},
        )

    def clone(self, source_id: str, name: str, location: str) -> dict:
        """POST /vms — clone an existing VM."""
        return self._request(
            "POST",
            "/vms",
            json={"parentId": source_id, "name": name, "location": location},
        )

    def delete(self, vm_id: str) -> None:
        """DELETE /vms/{id} — unregister and delete a VM."""
        self._request("DELETE", f"/vms/{vm_id}")

    def register(self, path: str, name: str) -> dict:
        """POST /vms/registration — register an existing VMX file."""
        return self._request(
            "POST",
            "/vms/registration",
            json={"path": path, "name": name},
        )

    # Power

    def get_power_state(self, vm_id: str) -> dict:
        """GET /vms/{id}/power — return current power state."""
        return self._request("GET", f"/vms/{vm_id}/power")

    def set_power_state(self, vm_id: str, state: str) -> dict:
        """PUT /vms/{id}/power — set power state.

        Valid states: ``"on"``, ``"off"``, ``"shutdown"``, ``"suspend"``,
        ``"pause"``, ``"unpause"``.
        """
        return self._request("PUT", f"/vms/{vm_id}/power", data=state)

    # Networking

    def get_ip(self, vm_id: str) -> dict:
        """GET /vms/{id}/ip — return the guest IP address."""
        return self._request("GET", f"/vms/{vm_id}/ip")

    def get_nic_ips(self, vm_id: str) -> dict:
        """GET /vms/{id}/nicips — return IPs for each NIC."""
        return self._request("GET", f"/vms/{vm_id}/nicips")

    def list_nics(self, vm_id: str) -> list[dict]:
        """GET /vms/{id}/nic — list NIC devices."""
        return self._request("GET", f"/vms/{vm_id}/nic")

    def create_nic(self, vm_id: str, type: str, vmnet: str) -> dict:
        """POST /vms/{id}/nic — add a NIC to the VM."""
        return self._request(
            "POST",
            f"/vms/{vm_id}/nic",
            json={"type": type, "vmnet": vmnet},
        )

    def update_nic(self, vm_id: str, index: int, type: str, vmnet: str) -> dict:
        """PUT /vms/{id}/nic/{index} — update an existing NIC."""
        return self._request(
            "PUT",
            f"/vms/{vm_id}/nic/{index}",
            json={"type": type, "vmnet": vmnet},
        )

    def delete_nic(self, vm_id: str, index: int) -> None:
        """DELETE /vms/{id}/nic/{index} — remove a NIC."""
        self._request("DELETE", f"/vms/{vm_id}/nic/{index}")

    # Shared folders

    def list_shared_folders(self, vm_id: str) -> list[dict]:
        """GET /vms/{id}/sharedfolders — list shared folders."""
        return self._request("GET", f"/vms/{vm_id}/sharedfolders")

    def mount_shared_folder(
        self,
        vm_id: str,
        host_path: str,
        guest_path: str,
        flags: int = 0,
    ) -> dict:
        """POST /vms/{id}/sharedfolders — mount a shared folder."""
        return self._request(
            "POST",
            f"/vms/{vm_id}/sharedfolders",
            json={"host_path": host_path, "guest_path": guest_path, "flags": flags},
        )

    def update_shared_folder(
        self,
        vm_id: str,
        folder_id: str,
        host_path: str,
        flags: int = 0,
    ) -> dict:
        """PUT /vms/{id}/sharedfolders/{folder_id} — update a shared folder."""
        return self._request(
            "PUT",
            f"/vms/{vm_id}/sharedfolders/{folder_id}",
            json={"host_path": host_path, "flags": flags},
        )

    def delete_shared_folder(self, vm_id: str, folder_id: str) -> None:
        """DELETE /vms/{id}/sharedfolders/{folder_id} — remove a shared folder."""
        self._request("DELETE", f"/vms/{vm_id}/sharedfolders/{folder_id}")

    # Params / restrictions

    def get_param(self, vm_id: str, name: str) -> dict:
        """GET /vms/{id}/params/{name} — get a single VM parameter."""
        return self._request("GET", f"/vms/{vm_id}/params/{name}")

    def update_params(self, vm_id: str, params: dict[str, str]) -> dict:
        """PUT /vms/{id}/params — update multiple VM parameters."""
        return self._request("PUT", f"/vms/{vm_id}/params", json=params)

    def get_restrictions(self, vm_id: str) -> dict:
        """GET /vms/{id}/restrictions — get VM restriction settings."""
        return self._request("GET", f"/vms/{vm_id}/restrictions")


# ---------------------------------------------------------------------------
# _NetworkModule
# ---------------------------------------------------------------------------


class _NetworkModule:
    """Methods under /api/vmnet — accessible as ``vmrest.network.*``."""

    def __init__(self, request: _Requester) -> None:
        self._request = request

    def list_vmnets(self) -> dict:
        """GET /vmnet — list all virtual networks."""
        return self._request("GET", "/vmnet")

    def create_vmnet(
        self,
        name: str,
        type: str,
        subnet: str,
        mask: str,
    ) -> dict:
        """POST /vmnets — create a new virtual network."""
        return self._request(
            "POST",
            "/vmnets",
            json={"name": name, "type": type, "subnet": subnet, "mask": mask},
        )

    def list_mac_to_ip(self, vmnet: str) -> dict:
        """GET /vmnet/{vmnet}/mactoip — list static MAC-to-IP mappings."""
        return self._request("GET", f"/vmnet/{vmnet}/mactoip")

    def update_mac_to_ip(self, vmnet: str, mac: str, ip: str) -> dict:
        """PUT /vmnet/{vmnet}/mactoip/{mac} — set or update a MAC-to-IP mapping."""
        return self._request(
            "PUT",
            f"/vmnet/{vmnet}/mactoip/{mac}",
            json={"IP": ip},
        )

    def list_port_forwards(self, vmnet: str) -> dict:
        """GET /vmnet/{vmnet}/portforward — list port-forwarding rules."""
        return self._request("GET", f"/vmnet/{vmnet}/portforward")

    def update_port_forward(
        self,
        vmnet: str,
        protocol: str,
        port: int,
        host_ip: str,
        guest_ip: str,
        guest_port: int,
        desc: str = "",
    ) -> dict:
        """PUT /vmnet/{vmnet}/portforward/{protocol}/{port} — add/update a port-forward rule."""
        return self._request(
            "PUT",
            f"/vmnet/{vmnet}/portforward/{protocol}/{port}",
            json={
                "guestIp": guest_ip,
                "guestPort": guest_port,
                "desc": desc,
            },
        )

    def delete_port_forward(self, vmnet: str, protocol: str, port: int) -> None:
        """DELETE /vmnet/{vmnet}/portforward/{protocol}/{port} — remove a port-forward rule."""
        self._request("DELETE", f"/vmnet/{vmnet}/portforward/{protocol}/{port}")


# ---------------------------------------------------------------------------
# VMRest
# ---------------------------------------------------------------------------


class VMRest:
    """Python wrapper for the vmrest REST API.

    Parameters
    ----------
    username:
        Credential configured via ``vmrest -C``.
    password:
        Credential configured via ``vmrest -C``.
    base_url:
        Base URL of the vmrest server (default ``http://127.0.0.1:8697``).
    timeout:
        Request timeout in seconds (default 30).

    Attributes
    ----------
    vms:
        VM management sub-module (:class:`_VMsModule`).
    network:
        Virtual network sub-module (:class:`_NetworkModule`).
    """

    DEFAULT_BASE_URL = "http://127.0.0.1:8697"

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers["Accept"] = "application/vnd.vmware.vmw.rest-v1+json"

        self.vms = _VMsModule(self._request)
        self.network = _NetworkModule(self._request)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}/api{path}"
        kwargs.setdefault("timeout", self._timeout)
        try:
            resp = self._session.request(method, url, **kwargs)
        except requests.ConnectionError as exc:
            raise VMRestConnectionError(0, str(exc)) from exc
        except requests.Timeout as exc:
            raise VMRestConnectionError(0, f"Timeout after {self._timeout}s") from exc

        if resp.ok:
            return resp.json() if resp.content else None

        body = resp.json() if resp.content else {}
        msg = body.get("Message", resp.reason)
        exc_class = _STATUS_MAP.get(resp.status_code, VMRestServerError)
        raise exc_class(resp.status_code, msg)

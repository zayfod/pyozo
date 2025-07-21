"""

Utility functions for connecting to robots over Bluetooth.

"""

from typing import AsyncGenerator, List
from contextlib import asynccontextmanager

from bleak import BleakScanner, BleakClient

from .robot import Robot


__all__ = [
    "get_robot",
    "discover_robots",
]


@asynccontextmanager
async def get_robot(name: str = "", uuid: str = "", timeout: float = 3.0) -> AsyncGenerator[Robot, None]:
    """Connect to a specific robot by name or UUID, or connect to the first availble one."""
    if name:
        device = await BleakScanner.find_device_by_name(name, timeout=timeout)
    elif uuid:
        device = await BleakScanner.find_device_by_address(uuid, timeout=timeout)
    else:
        devices = await BleakScanner(timeout=timeout).discover()
        sorted_devices = sorted(devices, key=lambda device: (device.name or "", device.address))
        for device in sorted_devices:
            if device.name and device.name.startswith("Ozo"):
                break
        else:
            device = None

    if device is None:
        raise RuntimeError("Failed to find robot.")

    async with BleakClient(device) as client:
        async with Robot(client) as robot:
            yield robot


async def discover_robots(timeout: float = 3.0) -> List[str]:
    """Return a list of available robot UUID addresses through Bluetooth discovery."""
    devices = await BleakScanner(timeout=timeout).discover()
    sorted_devices = sorted(devices, key=lambda device: (device.name or "", device.address))
    res = []
    for device in sorted_devices:
        if device.name and device.name.startswith("Ozo"):
            res.append(device.address)
    return res

#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        print("Name: {}".format(await robot.get_name()))
        print("S/N: {}".format(await robot.get_serial_number()))
        print("Firmware version: {}".format(await robot.get_fw_version()))
        print("Bluetooth version: {}".format(await robot.get_bluetooth_version()))


asyncio.run(main())

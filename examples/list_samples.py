#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        files = await robot.fts.listdir("/system/audio")
        for file in files:
            print(f"{file.name}\t{file.size / 1024:0.02f} kB")


asyncio.run(main())

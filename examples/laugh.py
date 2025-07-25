#!/usr/bin/env python3
"""

Play a laugh sample on the robot.

"""

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        # TODO: Detect disabled speaker when charging.

        await robot.cts.execute_file("/system/audio/01010100.wav")


asyncio.run(main())

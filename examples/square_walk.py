#!/usr/bin/env python3
"""

Move in a square.

"""

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        for _ in range(4):
            await robot.cts.move_straight(0.05, 0.12)
            await asyncio.sleep(1.0)
            await robot.rotate_deg(90, 120)
            await asyncio.sleep(1.0)  # TODO: Wait for events.


asyncio.run(main())

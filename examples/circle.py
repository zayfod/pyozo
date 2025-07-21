#!/usr/bin/env python3
"""

Move in circle.

"""

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        await robot.move_wheels(0.08, 0.04, 3500)


asyncio.run(main())

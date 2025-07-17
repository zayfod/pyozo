#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        # TODO: Detect disabled proximity sensors when charging.

        while True:
            print(await robot.get_ir_proximity())
            await asyncio.sleep(0.25)


asyncio.run(main())

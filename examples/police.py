#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        await robot.cts.set_led(pyozo.Lights.ALL_ROBOT)
        for _ in range(3):
            for _ in range(6):
                await robot.cts.set_led(pyozo.Lights.FRONT_1 | pyozo.Lights.FRONT_2, 200, 0, 0)
                await asyncio.sleep(0.05)
                await robot.cts.set_led(pyozo.Lights.FRONT_1 | pyozo.Lights.FRONT_2, 0, 0, 0)
                await asyncio.sleep(0.02)
            for _ in range(6):
                await robot.cts.set_led(pyozo.Lights.FRONT_4 | pyozo.Lights.FRONT_5, 0, 0, 200)
                await asyncio.sleep(0.05)
                await robot.cts.set_led(pyozo.Lights.FRONT_4 | pyozo.Lights.FRONT_5, 0, 0, 0)
                await asyncio.sleep(0.02)
        await robot.cts.set_led(pyozo.Lights.ALL_ROBOT)


asyncio.run(main())

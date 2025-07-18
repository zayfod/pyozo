#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        while True:
            # Read processed color from sensor.
            color = await robot.get_processed_color()
            await robot.cts.set_led(pyozo.Lights.ALL_FRONT, color.red, color.green, color.blue)

        # TODO: Turn off LEDs on disconnect.


asyncio.run(main())

#!/usr/bin/env python3
"""

Simple obstacle avoidance using IR proximity sensors.

"""

import asyncio

import pyozo


PROXIMITY_THRESHOLD = 80
MOVE_SPEED = 0.05
MOVE_DURATION = 200
TURN_SPEED = 0.03
TURN_DURATION = 200


async def main() -> None:
    async with pyozo.get_robot() as robot:
        while True:

            proximity = await robot.get_ir_proximity()

            if proximity.left_front > PROXIMITY_THRESHOLD and proximity.right_front <= PROXIMITY_THRESHOLD:
                print("Turning right to avoid left obstacle.")
                await robot.move_wheels(TURN_SPEED, -TURN_SPEED, duration_ms=TURN_DURATION)
            elif proximity.left_front <= PROXIMITY_THRESHOLD and proximity.right_front > PROXIMITY_THRESHOLD:
                print("Turning left to avoid right obstacle.")
                await robot.move_wheels(-TURN_SPEED, TURN_SPEED, duration_ms=TURN_DURATION)
            elif proximity.left_front > PROXIMITY_THRESHOLD and proximity.right_front > PROXIMITY_THRESHOLD:
                print("Turning right (default) to avoid forward obstacle.")
                await robot.move_wheels(-TURN_SPEED, TURN_SPEED, duration_ms=TURN_DURATION)
            else:
                print("No obstacles. Moving forward.")
                await robot.move_wheels(MOVE_SPEED, MOVE_SPEED, duration_ms=MOVE_DURATION)


asyncio.run(main())

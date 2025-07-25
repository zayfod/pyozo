#!/usr/bin/env python3
"""

Simple maze navigation.

"""

import asyncio

import pyozo


async def main() -> None:
    async with pyozo.get_robot() as robot:
        await robot.set_line_navigation_speed(0.03)

        direction = await robot.cts.line_navigation(
            pyozo.IntersectionDirection.STRAIGHT, pyozo.LineNavigationAction.FOLLOW
        )

        cnt = 0
        while cnt < 50:
            print(f"Intersection: {direction}")

            if pyozo.IntersectionDirection.LEFT in direction:
                print("Turning left!")
                await robot.cts.execute_file("/system/audio/01040102.wav")  # Say "left".
                direction = await robot.cts.line_navigation(
                    pyozo.IntersectionDirection.LEFT, pyozo.LineNavigationAction.FOLLOW
                )
            elif pyozo.IntersectionDirection.STRAIGHT in direction:
                print("Going forward!")
                await robot.cts.execute_file("/system/audio/01040101.wav")  # Say "forward".
                direction = await robot.cts.line_navigation(
                    pyozo.IntersectionDirection.STRAIGHT, pyozo.LineNavigationAction.FOLLOW
                )
            elif pyozo.IntersectionDirection.RIGHT in direction:
                print("Turning right!")
                await robot.cts.execute_file("/system/audio/01040104.wav")  # Say "right".
                direction = await robot.cts.line_navigation(
                    pyozo.IntersectionDirection.RIGHT, pyozo.LineNavigationAction.FOLLOW
                )
            elif pyozo.IntersectionDirection.BACKWARD in direction:
                print("Turning back!")
                await robot.cts.execute_file("/system/audio/01040108.wav")  # Say "back".
                direction = await robot.cts.line_navigation(
                    pyozo.IntersectionDirection.BACKWARD, pyozo.LineNavigationAction.FOLLOW
                )
            else:
                print("I am stuck!")
                await robot.cts.execute_file("/system/audio/01010110.wav")  # "Sad" sound.
                break

            cnt += 1


asyncio.run(main())

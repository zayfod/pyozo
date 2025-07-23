#!/usr/bin/env python3
"""

Simple maze navigation.

"""

import asyncio

import pyozo


async def line_navigation_update_handler(
    robot: pyozo.Robot, request_id: int, state: pyozo.ExecutionState, direction: pyozo.IntersectionDirection
) -> None:
    if state != pyozo.ExecutionState.FINISHED_NORMAL:
        return

    print(f"Intersection: {direction}")

    if pyozo.IntersectionDirection.LEFT in direction:
        print("Turning left!")
        await robot.cts.execute_file("/system/audio/01040102.wav")  # Say "left".
        await asyncio.sleep(1.0)
        await robot.cts.line_navigation(pyozo.IntersectionDirection.LEFT, pyozo.LineNavigationAction.FOLLOW)
    elif pyozo.IntersectionDirection.STRAIGHT in direction:
        print("Going forward!")
        await robot.cts.execute_file("/system/audio/01040101.wav")  # Say "forward".
        await asyncio.sleep(1.0)
        await robot.cts.line_navigation(pyozo.IntersectionDirection.STRAIGHT, pyozo.LineNavigationAction.FOLLOW)
    elif pyozo.IntersectionDirection.RIGHT in direction:
        print("Turning right!")
        await robot.cts.execute_file("/system/audio/01040104.wav")  # Say "right".
        await asyncio.sleep(1.0)
        await robot.cts.line_navigation(pyozo.IntersectionDirection.RIGHT, pyozo.LineNavigationAction.FOLLOW)
    elif pyozo.IntersectionDirection.BACKWARD in direction:
        print("Turning back!")
        await robot.cts.execute_file("/system/audio/01040108.wav")  # Say "back".
        await asyncio.sleep(1.0)
        await robot.cts.line_navigation(pyozo.IntersectionDirection.BACKWARD, pyozo.LineNavigationAction.FOLLOW)
    else:
        print("I am stuck!")
        await robot.cts.execute_file("/system/audio/01010110.wav")  # "Sad" sound.


async def main() -> None:
    async with pyozo.get_robot() as robot:
        await robot.set_line_navigation_update_handler(line_navigation_update_handler)
        await robot.set_line_navigation_speed(0.03)
        await robot.cts.line_navigation(pyozo.IntersectionDirection.STRAIGHT, pyozo.LineNavigationAction.FOLLOW)
        await asyncio.sleep(60.0)


asyncio.run(main())

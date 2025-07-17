#!/usr/bin/env python3

import asyncio

import pyozo


async def main() -> None:
    print("Scanning for robots...")
    robot_uuids = await pyozo.discover_robots()

    print()

    if robot_uuids:
        print("Discovered robots:")
        for robot_uuid in robot_uuids:
            print(f"- {robot_uuid}")
    else:
        print("No robots found.")


asyncio.run(main())

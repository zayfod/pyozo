#!/usr/bin/env python3
"""

Watcher use.

"""

import logging
import asyncio

import pyozo


async def main() -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.DEBUG)
    logging.getLogger("bleak").setLevel(logging.WARNING)

    async with pyozo.get_robot() as robot:
        # Print available number of watchers.
        print(await robot.get_watchers_info())

        # Enable watcher for processed color.
        await robot.cts.watcher_region_setup(1, 1, pyozo.PROCESSED_COLOR_ADDRESS, pyozo.PROCESSED_COLOR_SIZE)
        await robot.cts.watcher_setup(
            1,
            pyozo.WatcherFlags.ENABLED | pyozo.WatcherFlags.DISABLE_WHEN_DISCONNECTED,
            1000,
            1000,
        )

        # TODO: Robot API and event handling needed.

        await asyncio.sleep(10.0)

        # Disable watcher.
        await robot.cts.watcher_setup(1, pyozo.WatcherFlags(0), 0, 0)
        await robot.cts.watcher_region_setup(1, 0, 0, 0)


asyncio.run(main())

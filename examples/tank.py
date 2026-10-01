#!/usr/bin/env python3
"""

Pygame keyboard controlled tank.

"""

import asyncio

import pygame

import pyozo


MOVE_SPEED = 0.06
TURN_SPEED = 0.03


async def main() -> None:
    pygame.init()
    pygame.display.set_mode((640, 480))
    pygame.display.set_caption("pyozo tank")

    left_speed = 0.0
    right_speed = 0.0

    async with pyozo.get_robot() as robot:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    print(f"Key pressed: {pygame.key.name(event.key)}")
                    if event.key == pygame.K_w:
                        left_speed += MOVE_SPEED
                        right_speed += MOVE_SPEED
                    elif event.key == pygame.K_s:
                        left_speed -= MOVE_SPEED
                        right_speed -= MOVE_SPEED
                    elif event.key == pygame.K_a:
                        left_speed -= TURN_SPEED
                        right_speed += TURN_SPEED
                    elif event.key == pygame.K_d:
                        left_speed += TURN_SPEED
                        right_speed -= TURN_SPEED
                    elif event.key == pygame.K_q:
                        running = False
                elif event.type == pygame.KEYUP:
                    print(f"Key released: {pygame.key.name(event.key)}")
                    if event.key == pygame.K_w:
                        left_speed -= MOVE_SPEED
                        right_speed -= MOVE_SPEED
                    elif event.key == pygame.K_s:
                        left_speed += MOVE_SPEED
                        right_speed += MOVE_SPEED
                    elif event.key == pygame.K_a:
                        left_speed += TURN_SPEED
                        right_speed -= TURN_SPEED
                    elif event.key == pygame.K_d:
                        left_speed -= TURN_SPEED
                        right_speed += TURN_SPEED

                await robot.move_wheels(left_speed, right_speed)

            await asyncio.sleep(0.1)  # Limit to 10 FPS

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())

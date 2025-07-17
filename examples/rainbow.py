#!/usr/bin/env python3

from typing import List, Tuple, Generator
import asyncio
import colorsys

import pyozo


class RainbowGenerator:
    """Generates a sequence of RGB color values that cycle through the rainbow."""

    def __init__(
        self,
        num_leds: int,
        saturation: float = 1.0,
        lightness: float = 0.5,
        hue_start: float = 0.0,
        hue_end: float = 1.0,
    ) -> None:
        """
        Initializes the RainbowGenerator.

        Args:
            num_leds (int): The number of LEDs in your animation strip/device.
                            This helps distribute the colors smoothly.
            saturation (float): The saturation component of the HSL color model (0.0 to 1.0).
                                1.0 is fully saturated (vivid colors).
            lightness (float): The lightness component of the HSL color model (0.0 to 1.0).
                                0.5 is typically good for vibrant colors.
            hue_start (float): The starting hue value (0.0 to 1.0). 0.0 is red.
            hue_end (float): The ending hue value (0.0 to 1.0). 1.0 is also red (cycles back).
        """
        self.num_leds = num_leds
        self.saturation = saturation
        self.lightness = lightness
        self.hue_start = hue_start
        self.hue_end = hue_end
        self._current_hue = hue_start

    def _hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[int, int, int]:  # noqa: E741
        """Converts HSL color values to RGB (0-255 range)."""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    def generate_colors(self, steps_per_cycle: int = 360) -> Generator[List[Tuple[int, int, int]], None, None]:
        """
        A generator that yields RGB color tuples (R, G, B) for a rainbow animation.

        Args:
            steps_per_cycle (int): The number of steps (frames) to complete one full rainbow cycle.
                                   Higher values mean smoother, slower transitions.
        Yields:
            tuple: An (R, G, B) tuple, where each component is an integer from 0 to 255.
        """
        hue_range = self.hue_end - self.hue_start
        hue_step = hue_range / steps_per_cycle

        while True:
            # Generate colors for each LED in the strip, with a slight offset
            # to create the "rainbow wave" effect.
            colors_for_frame = []
            for i in range(self.num_leds):
                # Offset hue for each LED to create a spread of colors
                # The 0.1 / self.num_leds creates a small phase shift across the LEDs
                effective_hue = (self._current_hue + (i * (hue_range / self.num_leds) * 0.5)) % 1.0
                r, g, b = self._hsl_to_rgb(effective_hue, self.saturation, self.lightness)
                colors_for_frame.append((r, g, b))
            yield colors_for_frame

            self._current_hue = (self._current_hue + hue_step) % 1.0


async def main() -> None:
    gen = RainbowGenerator(
        num_leds=5,
        saturation=1.0,
        lightness=0.5,
        hue_start=0.0,  # Start with red
        hue_end=1.0,  # Cycle back to red
    )

    async with pyozo.get_robot() as robot:
        color_frames = gen.generate_colors(steps_per_cycle=100)
        while True:
            for _ in range(300):
                color_frame = next(color_frames)
                colors = color_frame[0]
                await robot.cts.set_led(led_mask=pyozo.Lights.FRONT_1, red=colors[0], green=colors[1], blue=colors[2])
                colors = color_frame[1]
                await robot.cts.set_led(led_mask=pyozo.Lights.FRONT_2, red=colors[0], green=colors[1], blue=colors[2])
                colors = color_frame[2]
                await robot.cts.set_led(led_mask=pyozo.Lights.FRONT_3, red=colors[0], green=colors[1], blue=colors[2])
                colors = color_frame[3]
                await robot.cts.set_led(led_mask=pyozo.Lights.FRONT_4, red=colors[0], green=colors[1], blue=colors[2])
                colors = color_frame[4]
                await robot.cts.set_led(led_mask=pyozo.Lights.FRONT_5, red=colors[0], green=colors[1], blue=colors[2])
                await asyncio.sleep(0.01)

        # TODO: Turn off LEDs on disconnect.


asyncio.run(main())

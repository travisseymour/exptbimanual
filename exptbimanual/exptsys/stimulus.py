"""
This file is part of the exptbimanual source code.
Copyright (C) 2025 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from functools import partial, update_wrapper, lru_cache
from typing import Callable


import pygame


def return_partial(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return partial(func, *args, **kwargs)

    update_wrapper(wrapper, func)  # Preserve signature and docstring
    return wrapper


@lru_cache(maxsize=128)
def text_to_surface(text: str, font_name: str, font_size: int, color: str) -> pygame.Surface:
    """
    Return a rendered text surface, cached to avoid redundant rendering.
    """
    font = pygame.font.SysFont(font_name, font_size)
    color_obj = pygame.Color(color)
    return font.render(text, True, color_obj)


def draw_image(screen: pygame.Surface, image: pygame.Surface, position: tuple, center_on_position: bool = True):
    """
    Blit image onto screen at specified position.
    If center_on_position, adjust position so that center of image is at position.
    """
    if center_on_position:
        rect = image.get_rect(center=position)
    else:
        rect = image.get_rect(topleft=position)

    screen.blit(image, rect)


def draw_text(
    screen: pygame.Surface,
    text: str,
    position: tuple[int, int],
    center_on_position: bool = True,
    font: tuple[str, int] = ("Arial", 14),
    color="white",
):
    """
    Draw text onto screen at specified position.
    If center_on_position, adjust position so that center of the string is at position.
    """
    font_name, font_size = font
    text_surface = text_to_surface(text, font_name, font_size, color)

    if center_on_position:
        rect = text_surface.get_rect(center=position)
    else:
        rect = text_surface.get_rect(topleft=position)

    screen.blit(text_surface, rect)


def draw_multiline_text(
    screen: pygame.Surface,
    text: str,
    position: tuple[int, int],
    font: tuple[str, int] = ("Arial", 14),
    color="white",
    center_vertically: bool = True,
    center_horizontally: bool = True,
):
    """
    Draw multi-line text onto screen at the specified position.
    - If center_vertically is True, the block of text is vertically centered around position[1].
    - If center_horizontally is True, each line is centered around position[0].
    Otherwise, text is aligned to top-left.
    """
    font_name, font_size = font
    lines = text.splitlines()
    line_surfaces = [text_to_surface(line, font_name, font_size, color) for line in lines]

    line_height = line_surfaces[0].get_height() if line_surfaces else 0
    total_height = len(line_surfaces) * line_height

    x, y = position
    if center_vertically:
        y -= total_height // 2

    for surface in line_surfaces:
        line_width = surface.get_width()
        if center_horizontally:
            rect = surface.get_rect(center=(x, y + line_height // 2))
        else:
            rect = surface.get_rect(topleft=(x, y))
        screen.blit(surface, rect)
        y += line_height


def play_sound(sound: pygame.mixer.Sound, wait: bool = False, volume: float = 1.0):
    """
    Play a previously loaded sound.
    If duration is 0, use sound.get_length() to set duration.
    Should work with wav, mp3, ogg.
    Volume must be between 0.0 and 1.0
    """
    sound.set_volume(volume)

    sound.play()
    if wait:
        wait_ms = int(sound.get_length() * 1000)
        elapsed = 0
        tick = 50  # polling interval in ms

        while elapsed < wait_ms and pygame.mixer.get_busy():
            pygame.time.delay(tick)
            elapsed += tick

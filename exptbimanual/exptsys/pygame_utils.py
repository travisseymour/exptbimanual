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

import pygame


def scale_image(original_image: pygame.surface, size: tuple[int, int]) -> pygame.surface:
    return pygame.transform.smoothscale(original_image, size)


def scale_surface(original_surface: pygame.Surface, scale_factor: float) -> pygame.Surface:
    """
    Returns a new surface scaled by `scale_factor`.

    Args:
        original_surface: The Pygame surface to scale.
        scale_factor: Scaling factor (e.g., 0.5 for 50%, 2.0 for 200%).

    Returns:
        A new scaled Pygame surface.
    """
    original_width, original_height = original_surface.get_size()
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    return pygame.transform.smoothscale(original_surface, (new_width, new_height))

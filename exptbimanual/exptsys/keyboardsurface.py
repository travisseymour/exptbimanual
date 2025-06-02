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

from functools import lru_cache

import pygame

# Define the full keyboard layout (simplified)
KEY_LAYOUT = [
    list("1234567890"),
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
]

SPECIAL_KEYS = {
    "SPACE": {"label": "Space", "width": 6},  # 6x regular key width
}

KEY_WIDTH = 60
KEY_HEIGHT = 60
KEY_SPACING = 10
MARGIN = 20
FONT_SIZE = 28


@lru_cache(20)
def keyboard_surface(keys_to_highlight: str, highlight_color: tuple = (100, 255, 100)) -> pygame.Surface:
    pygame.init()
    font = pygame.font.SysFont("Arial", FONT_SIZE)

    rows = len(KEY_LAYOUT) + 1  # +1 for spacebar
    cols = max(len(row) for row in KEY_LAYOUT)
    surface_width = MARGIN * 2 + cols * (KEY_WIDTH + KEY_SPACING) - KEY_SPACING
    surface_height = MARGIN * 2 + rows * (KEY_HEIGHT + KEY_SPACING) - KEY_SPACING

    surface = pygame.Surface((surface_width, surface_height))
    surface.fill((30, 30, 30))

    key_color = (200, 200, 200)
    text_color = (0, 0, 0)

    keys_to_highlight = {k.upper() for k in keys_to_highlight.split(" ")}

    for row_idx, row in enumerate(KEY_LAYOUT):
        offset = (cols - len(row)) * (KEY_WIDTH + KEY_SPACING) // 2  # center short rows
        for col_idx, key in enumerate(row):
            x = MARGIN + offset + col_idx * (KEY_WIDTH + KEY_SPACING)
            y = MARGIN + row_idx * (KEY_HEIGHT + KEY_SPACING)

            rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)
            color = highlight_color if key.upper() in keys_to_highlight else key_color
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, (0, 0, 0), rect, width=2, border_radius=8)

            text = font.render(key.upper(), True, text_color)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

    # Draw spacebar on final row
    spacebar_row = len(KEY_LAYOUT)
    spacebar_width = SPECIAL_KEYS["SPACE"]["width"] * KEY_WIDTH + (SPECIAL_KEYS["SPACE"]["width"] - 1) * KEY_SPACING
    spacebar_x = (surface_width - spacebar_width) // 2
    spacebar_y = MARGIN + spacebar_row * (KEY_HEIGHT + KEY_SPACING)

    spacebar_rect = pygame.Rect(spacebar_x, spacebar_y, spacebar_width, KEY_HEIGHT)
    color = highlight_color if "SPACE" in keys_to_highlight else key_color
    pygame.draw.rect(surface, color, spacebar_rect, border_radius=8)
    pygame.draw.rect(surface, (0, 0, 0), spacebar_rect, width=2, border_radius=8)

    text = font.render("Space", True, text_color)
    text_rect = text.get_rect(center=spacebar_rect.center)
    surface.blit(text, text_rect)

    return surface


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 400))
    keys = "A S D SPACE 1 0 Z M"
    keyboard_image = keyboard_surface(keys)
    screen.blit(keyboard_image, (0, 0))
    pygame.display.flip()

    # Wait until closed
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

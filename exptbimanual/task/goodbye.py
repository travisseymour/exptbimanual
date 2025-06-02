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

import exptbimanual.task.task_setup as setup
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_text, draw_multiline_text

# Other globals
center_x, center_y = setup.options.screen_size
screen_center: tuple[int, int] = (center_x // 2, center_y // 2)
scratchpad: dict = {}


@return_partial
def draw_goodbye_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Experiment Complete!",
        position=(screen_center[0], setup.options.screen_size[1] - 100),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="Thank you for participating in our study.\nWe appreciate your help in our research.",
        position=(screen_center[0], 150),
        color="white",
        font=("Arial", 32),
    )

    return data


def run(screen: pygame.surface):
    screen.fill("black")
    pygame.display.flip()

    goodbye_screen_result = run_loop(
        screen,
        draw_goodbye_screen(screen),
        duration=30000,
        wait_for_responses=1,
        responses_allowed=["SPACE"],
    )

    # DEBUG
    # print(f"{goodbye_screen_result=}")

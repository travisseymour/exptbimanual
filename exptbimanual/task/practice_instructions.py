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

from types import SimpleNamespace

import pygame

import exptbimanual.task.task_setup as setup
from exptbimanual.exptsys.keyboardsurface import keyboard_surface
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_multiline_text, draw_text, draw_image

# Other globals
screen_width, screen_height = setup.options.screen_size
screen_center: tuple[int, int] = (screen_width // 2, screen_height // 2)
scratchpad: dict = {}


@return_partial
def welcome_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Welcome To Our Study!",
        position=(screen_center[0], 50),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="On the following screen, you will find instructions for our task.\n"
        "Please read each instruction screen carefully.\n"
        "If there is some instruction you don't understand,\n"
        "Please let the Experimenter know immediately.\n"
        "Press SPACEBAR To Continue",
        position=screen_center,
        color="white",
        font=("Arial", 32),
        center_vertically=True,
        center_horizontally=True,
    )

    return data


@return_partial
def one_key_practice_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Instructions",
        position=(screen_center[0], 50),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="In this task, you will some times need to press one of the\n"
        "keys highlighted below. On the computer keyboard, press\n"
        "either the A, S, K, or L keys.\n",
        position=(screen_center[0], screen_center[1] - 200),
        color="white",
        font=("Arial", 32),
        center_vertically=True,
        center_horizontally=True,
    )

    keyboard = keyboard_surface("A S K L")
    draw_image(
        screen=screen, image=keyboard, position=(screen_center[0], screen_height - keyboard.get_height() // 2 - 100)
    )

    return data


@return_partial
def two_key_practice_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Instructions",
        position=(screen_center[0], 50),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="In this task, you will some times need to press TWO keys\n"
        "at once. On the computer keyboard, press the keys\n"
        "A and K _simultaneously_.\n",
        position=(screen_center[0], screen_center[1] - 200),
        color="white",
        font=("Arial", 32),
        center_vertically=True,
        center_horizontally=True,
    )

    keyboard = keyboard_surface("A K")
    draw_image(
        screen=screen, image=keyboard, position=(screen_center[0], screen_height - keyboard.get_height() // 2 - 100)
    )

    return data


@return_partial
def sr_pairs_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Responses For Each Stimulus Pair",
        position=(screen_center[0], 50),
        color="lime",
        font=("Arial", 38),
    )

    # can convert SimpleNamespace to dict when accessing via str index is preferable
    sm = setup.media.__dict__

    sr_pairs = [
        SimpleNamespace(pics=[sm["FF1BW"], sm["HH1BW"]], responses=["A", "K"]),
        SimpleNamespace(pics=[sm["FF2BW"], sm["HH2BW"]], responses=["S", "L"]),
        SimpleNamespace(pics=[sm["FF3BW"], sm["HH1BW"]], responses=["K"]),
        SimpleNamespace(pics=[sm["FF1BW"], sm["HH3BW"]], responses=["A"]),
    ]

    list_left = 50
    list_top = 200
    pic_width = setup.media.FF1BW.get_width() + 10
    pic_height = setup.media.FF1BW.get_height() + 5

    for i, pair in enumerate(sr_pairs):
        draw_image(
            screen=screen, image=pair.pics[0], position=(list_left, list_top + pic_height * i), center_on_position=False
        )
        draw_image(
            screen=screen,
            image=pair.pics[1],
            position=(list_left + pic_width, list_top + pic_height * i),
            center_on_position=False,
        )
        draw_text(
            screen=screen,
            text=f"Response:  {str(pair.responses)}",
            position=(list_left + pic_width * 4, list_top + pic_height * i + pic_height // 2),
            center_on_position=True,
            font=("Arial", 32),
        )

    draw_text(
        screen=screen,
        text="Memorize and Then Press SPACEBAR",
        position=(screen_center[0], setup.options.screen_size[1] - 50),
        color="white",
        font=("Arial", 32),
    )

    return data


def run(screen: pygame.surface):
    screen.fill("black")
    pygame.display.flip()

    welcome_screen_result = run_loop(
        screen,
        welcome_screen(screen),
        wait_for_responses=1,
        responses_allowed=["SPACE"],
    )

    one_key_practice_result = run_loop(
        screen,
        one_key_practice_screen(screen),
        wait_for_responses=1,
        responses_allowed=list("ASKL"),
    )

    two_key_practice_result = run_loop(
        screen,
        two_key_practice_screen(screen),
        wait_for_responses=2,
        responses_allowed=list("ASKL"),
        correct_responses=list("AK"),
        exact_match=True,
    )

    sr_pair_screen_result = run_loop(
        screen,
        sr_pairs_screen(screen),
        wait_for_responses=1,
        responses_allowed=["SPACE"],
    )

    # DEBUG
    # print(f"{welcome_screen_result=}")
    # print(f"{one_key_practice_result=}")
    # print(f"{two_key_practice_result=}")
    # print(f"{sr_pair_screen_result=}")

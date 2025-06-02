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
from exptbimanual.exptsys.pygame_utils import scale_surface
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_image, draw_text, play_sound

# Other globals
screen_width, screen_height = setup.options.screen_size
screen_center: tuple[int, int] = (screen_width // 2, screen_height // 2)
scratchpad: dict = {}


@return_partial
def draw_fixation(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="+",
        position=screen_center,
        color="white",
        font=("Arial", 40),
        center_on_position=True,
    )

    return data


@return_partial
def draw_feedback(
    screen: pygame.Surface,
    keys: list[str],
    correct: bool,
    left_pic: pygame.Surface,
    right_pic: pygame.Surface,
    scratch: dict,
) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="CORRECT!" if correct else "Incorrect.",
        position=(screen_center[0], 50),
        color="lime" if correct else "red",
        font=("Arial", 40),
        center_on_position=True,
    )

    # Show 2 Images
    center_x, center_y = screen_center
    image_offset_x = 150
    draw_image(screen=screen, image=left_pic, position=(center_x - image_offset_x, center_y))
    draw_image(screen=screen, image=right_pic, position=(center_x + image_offset_x, center_y))

    keyboard = scale_surface(keyboard_surface(" ".join(keys)), scale_factor=0.5)
    draw_image(
        screen=screen, image=keyboard, position=(screen_center[0], screen_height - keyboard.get_height() // 2 - 50)
    )

    # NOTE: this isn't working
    # play sound once by setting a flag in the scratch dict
    if not scratch["feedback_played_sound"]:
        play_sound(sound=setup.media.beep_high if correct else setup.media.beep_low, wait=True, volume=0.2)
        scratch["feedback_played_sound"] = True

    return data


@return_partial
def draw_practice_screen(screen: pygame.Surface, left_pic: pygame.Surface, right_pic: pygame.Surface) -> dict:
    data = {}

    # Show fixation
    draw_text(
        screen=screen,
        text="+",
        position=screen_center,
        color="white",
        font=("Arial", 40),
        center_on_position=True,
    )

    # Show 2 Images
    center_x, center_y = screen_center
    image_offset_x = 150
    draw_image(screen=screen, image=left_pic, position=(center_x - image_offset_x, center_y))
    draw_image(screen=screen, image=right_pic, position=(center_x + image_offset_x, center_y))

    return data


def run(screen: pygame.surface):
    """
    This currently isn't any real task, I just made these trials up as a demo
    """
    global scratchpad

    screen.fill("black")
    pygame.display.flip()

    practice_data: list[dict] = []

    trial_types = [
        SimpleNamespace(stims=["FF1BW", "HH1BW"], pics=[setup.media.FF1BW, setup.media.HH1BW], correct=["A", "K"]),
        SimpleNamespace(stims=["FF2BW", "HH2BW"], pics=[setup.media.FF2BW, setup.media.HH2BW], correct=["S", "L"]),
        SimpleNamespace(stims=["FF3BW", "HH1BW"], pics=[setup.media.FF3BW, setup.media.HH1BW], correct=["K"]),
        SimpleNamespace(stims=["FF1BW", "HH3BW"], pics=[setup.media.FF1BW, setup.media.HH3BW], correct=["A"]),
    ]

    # 8 total trials for testing
    all_trials = trial_types * 2

    for trial in all_trials:
        _ = run_loop(screen, draw_fixation(screen), duration=1000)

        result = run_loop(
            screen,
            draw_practice_screen(screen, trial.pics[0], trial.pics[1]),
            wait_for_responses=1,  # seems odd, but I either want 1 resp or 2 SIMULTANEOUS responses
            responses_allowed=list("ASKL"),
            correct_responses=trial.correct,
            exact_match=True,
        )
        practice_data.append(result)

        # e.g.:
        # result=[
        #     {'display_func': 'draw_practice_screen', 'loop_start': 1975, 'stop': 2522, 'duration': 547,
        #      'responses': {
        #          InputRecord(type="keyboard", device="Kinesis Freestyle Edge Keyboard", key=A, time=29976.932),
        #          InputRecord(type="keyboard", device="Kinesis Freestyle Edge Keyboard", key=L, time=29976.934)
        #      }, 'correct_responses': ['A', 'K'], 'correct': False}]

        scratchpad["feedback_played_sound"] = False
        _ = run_loop(
            screen,
            draw_feedback(
                screen=screen,
                keys=trial.correct,
                correct="correct" in result and result["correct"],
                left_pic=trial.pics[0],
                right_pic=trial.pics[1],
                scratch=scratchpad,
            ),
            duration=4000,
        )

    # DEBUG
    print("PRACTICE DATA")
    print("-------------")
    for i, data in enumerate(practice_data):
        print(f"{i}. {data}")

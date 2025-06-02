import pygame

import exptbimanual.task.task_setup as setup
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_multiline_text, draw_text

# Other globals
center_x, center_y = setup.options.screen_size
screen_center: tuple[int, int] = (center_x // 2, center_y // 2)
scratchpad: dict = {}


@return_partial
def draw_screen1(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Welcome To Our Study!",
        position=(screen_center[0], 100),
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
def draw_screen2(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Instructions",
        position=(screen_center[0], 100),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="In this task, you will some times need to press one of the\n"
        "keys highlighted below. On the computer keyboard, press\n"
        "either the A, S, K, or L keys.\n",
        position=screen_center,
        color="white",
        font=("Arial", 32),
        center_vertically=True,
        center_horizontally=True,
    )

    return data


@return_partial
def draw_screen3(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Instructions",
        position=(screen_center[0], 100),
        color="lime",
        font=("Arial", 38),
    )

    draw_multiline_text(
        screen=screen,
        text="In this task, you will some times need to press TWO keys\n"
        "at once. On the computer keyboard, press the keys\n"
        "A and K _simultaneously_.\n",
        position=screen_center,
        color="white",
        font=("Arial", 32),
        center_vertically=True,
        center_horizontally=True,
    )

    return data


def run(screen: pygame.surface):
    screen.fill("black")
    pygame.display.flip()

    screen1_result = run_loop(
        screen,
        draw_screen1(screen),
        duration=5000,
        wait_for_responses=1,
        responses_allowed=["SPACE"],
    )

    screen2_result = run_loop(
        screen,
        draw_screen2(screen),
        duration=0,
        wait_for_responses=1,
        responses_allowed=list("ASKL"),
    )

    screen3_result = run_loop(
        screen,
        draw_screen3(screen),
        duration=0,
        wait_for_responses=2,
        responses_allowed=list("ASKL"),
        correct_response='AK'  # FIXME: should probably make this a list
    )

    # DEBUG
    print(f"{screen1_result=}")
    print(f"{screen2_result=}")
    print(f"{screen3_result=}")

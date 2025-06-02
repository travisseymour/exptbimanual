import pygame

import exptbimanual.task.task_setup as setup
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_image, draw_text

# Other globals
center_x, center_y = setup.options.screen_size
screen_center: tuple[int, int] = (center_x // 2, center_y // 2)
scratchpad: dict = {}


@return_partial
def draw_intro_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_text(
        screen=screen,
        text="Welcome To Our Study!",
        position=(screen_center[0], 150),
        color="lime",
        font=("Arial", 32),
    )

    draw_image(screen=screen, image=setup.media.keyboard_space, position=screen_center)

    draw_text(
        screen=screen,
        text="Press SPACEBAR To Begin",
        position=(screen_center[0], setup.options.screen_size[1] - 150),
        color="white",
        font=("Arial", 32),
    )

    return data


def run(screen: pygame.surface):
    screen.fill("black")
    pygame.display.flip()

    task_screen1 = run_loop(
        screen,
        draw_intro_screen(screen),
        duration=5000,
        wait_for_responses=1,
        responses_allowed=["SPACE"],
    )
    print(f"{task_screen1=}")

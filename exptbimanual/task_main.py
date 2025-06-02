from pathlib import Path
from types import SimpleNamespace

import pygame

import exptbimanual.task_setup as setup
from exptbimanual.exptsys.runner import run_loop
from exptbimanual.exptsys.stimulus import return_partial, draw_multiline_text, draw_image
from exptbimanual.resource import get_resource

# Preload Task Media
building_files = [f"HH{i + 1}BW.bmp" for i in range(6)]
face_files = [f"FF{i + 1}BW.bmp" for i in range(6)]
media = SimpleNamespace()

# Other globals
center_x, center_y = setup.options.screen_size
screen_center: tuple[int, int] = (center_x // 2, center_y // 2)
scratchpad: dict = {}


def preload_experiment_media():
    global media
    for file in building_files:
        setattr(media, Path(file).name, pygame.image.load(get_resource("images", "buildings", file)).convert_alpha())
    for file in face_files:
        setattr(media, Path(file).name, pygame.image.load(get_resource("images", "faces", file)).convert_alpha())
    media.keyboard_kl = pygame.image.load(get_resource("images", "response_box", "keyboard_as_kl.png"))
    media.keyboard_space = pygame.image.load(get_resource("images", "response_box", "keyboard_space.png"))
    media.beep_high = pygame.mixer.Sound(get_resource("sounds", "beep-high.wav"))
    media.beep_low = pygame.mixer.Sound(get_resource("sounds", "beep-low.wav"))

    print("Successfully preloaded media:")
    print(vars(media))


@return_partial
def draw_intro_screen(screen: pygame.Surface) -> dict:
    data = {}

    draw_multiline_text(
        screen=screen,
        text="Welcome To Our Study!\n"
        "On the following screen, you will find instructions for our task.\n"
        "Please read each instruction screen carefully.\n"
        "Press the SPACEBAR to Continue",
        position=(screen_center[0], 200),
        color="white",
        font=("Arial", 32),
        center_vertically=False,
        center_horizontally=True,
    )

    draw_image(screen=screen, image=media.keyboard_space, position=screen_center)

    return data


def task(screen: pygame.surface):
    """
    Run Main ExptBimanualTask.
    Assumes pygame is already setup!
    """

    screen.fill("black")
    pygame.display.flip()

    task_screen1 = run_loop(
        screen,
        draw_intro_screen(screen),
        duration=5000,
        wait_for_responses=1,
        responses_allowed=["SPACE", "A"],
        correct_response="SPACE",
    )
    print(f"{task_screen1=}")

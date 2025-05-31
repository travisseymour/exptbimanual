from functools import partial, update_wrapper, lru_cache
from typing import Callable
import pygame

from exptbimanual.exptsys.runner import run_loop
from exptbimanual.resource import get_resource


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


if __name__ == "__main__":
    import pygame

    """
    Quick Test of functions in this module
    """

    # Initialize mixer *before* display (safer for Linux audio backends)
    pygame.mixer.init()
    pygame.init()

    screen_size: tuple[int, int] = (1024, 768)
    screen_center: tuple[int, int] = (1024 // 2, 768 // 2)

    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("stimulus.py module test")

    screen.fill("black")
    pygame.display.flip()

    sound = pygame.mixer.Sound(get_resource("sounds", "beep-high.wav"))
    keyboard_image = pygame.image.load(get_resource("images", "response_box", "keyboard_space.png"))
    face_image = pygame.image.load(get_resource("images", "faces", "FF1BW.bmp"))
    building_image = pygame.image.load(get_resource("images", "buildings", "HH1BW.bmp"))

    scratchpad: dict = {"screen1_played_sound": False}

    @return_partial
    def draw_screen1(scratch: dict) -> dict:
        """
        This is just a way to test additions or changes to these stimulus functions
        """

        data = {}

        # test draw_text (as well as text flashing) by using the scratch dict to manage flashes
        draw_text(
            screen=screen,
            text="Press Spacebar To Continue",
            position=(screen_center[0], screen_size[1] - 150),
            color="lime",
            font=("Arial", 32),
        )

        # test draw_multiline_text by writing some text at the top of the screen
        draw_multiline_text(
            screen=screen,
            text="Welcome to this test of the\nstimulus.py module stimulus\ndrawing functions.",
            position=(screen_center[0], 100),
            color="white",
            font=("Arial", 32),
            center_vertically=False,
            center_horizontally=True,
        )

        # test draw_image by showing an image in the middle of the screen
        draw_image(screen=screen, image=keyboard_image, position=screen_center)

        # test play_sound (as well as transient sounds) by setting a flag in the scratch dict
        # that allows only playing the sound once
        if not scratch["screen1_played_sound"]:
            play_sound(sound=sound, wait=True, volume=0.2)
            scratch["screen1_played_sound"] = True

        return data

    @return_partial
    def draw_screen2(scratch: dict) -> dict:
        """
        This is just a way to test responses
        """

        data = {}

        # Response Instructions, made to blink every 500ms
        draw_text(
            screen=screen,
            text="Press F, J or Both",
            position=(screen_center[0], 200),
            color="white",
            font=("Arial", 32),
            center_on_position=True,
        )

        # Show 2 Images
        center_x, center_y = screen_center
        image_offset_x = 150
        draw_image(screen=screen, image=face_image, position=(center_x - image_offset_x, center_y))
        draw_image(screen=screen, image=building_image, position=(center_x + image_offset_x, center_y))

        return data

    # These will actually show the screens defined above
    task_screen1 = run_loop(screen, [draw_screen1(scratchpad)], duration=5000, wait_for_key=True)
    task_screen2 = run_loop(screen, [draw_screen2(scratchpad)], duration=0, wait_for_key=True)

    print(f"{task_screen1=}")
    print(f"{task_screen2=}")

    pygame.quit()
    pygame.mixer.quit()

from pathlib import Path
from types import SimpleNamespace

import FreeSimpleGUIQt as sg
import pygame
from fastnumbers import isfloat

from exptbimanual.apputils import set_qt_platform
from exptbimanual.resource import get_resource

building_files = [f"HH{i + 1}BW.bmp" for i in range(6)]
face_files = [f"FF{i + 1}BW.bmp" for i in range(6)]
media = SimpleNamespace()

options: SimpleNamespace = SimpleNamespace(
    bg_color="black", screen_size=(1024, 768), practice_blocks=1, test_blocks=1, keyboard_input=True, mouse_input=False
)


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


def get_parameters() -> dict:
    """
    A task specific dialog to obtain whatever session parameters are needed
    """
    font = ("Arial", 14)
    layout = [
        [sg.Text("Participant ID", font=font), sg.Input(key="subid", default_text="0", enable_events=True, font=font)],
        [sg.Text("Session #", font=font), sg.Input(key="session", default_text="1", enable_events=True, font=font)],
        [sg.Text(" ")],
        [sg.Button("Ok", key="Ok", disabled=False, font=font, bind_return_key=True), sg.Button("Quit", font=font)],
    ]

    window = sg.Window("Bimanual Experiment Task Setup", layout, finalize=True)
    window["Ok"].Widget.setStyleSheet("background-color: #cccccc; color: black")
    window["Quit"].Widget.setStyleSheet("background-color: #cccccc; color: black")

    def update_ok_button(enabled):
        if enabled:
            window["Ok"].update(disabled=False)
            window["Ok"].Widget.setStyleSheet("background-color: #cccccc; color: black")

        else:
            window["Ok"].update(disabled=True)
            window["Ok"].Widget.setStyleSheet("background-color: #cccccc; color: gray")

    def validate_inputs(values):
        subid_valid = isfloat(values.get("subid", "").strip())
        session_valid = isfloat(values.get("session", "").strip())

        window["subid"].update(background_color="white" if subid_valid else "#ffcccc")
        window["session"].update(background_color="white" if session_valid else "#ffcccc")

        update_ok_button(subid_valid and session_valid)

    # Perform initial validation
    validate_inputs(window.read(timeout=0)[1])

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Quit"):
            break

        if event in ("subid", "session"):
            validate_inputs(values)

        if event == "Ok":
            break

    window.close()
    if event == "Ok":
        return values
    else:
        return {}


if __name__ == "__main__":
    # testing
    set_qt_platform()
    print(get_parameters())

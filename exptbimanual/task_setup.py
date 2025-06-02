from types import SimpleNamespace

import FreeSimpleGUIQt as sg
from fastnumbers import isfloat

from exptbimanual.apputils import set_qt_platform

options: SimpleNamespace = SimpleNamespace(
    bg_color="black", screen_size=(1024, 768), practice_blocks=1, test_blocks=1, keyboard_input=True, mouse_input=False
)


def get_parameters() -> dict:
    """
    A task specific dialog to obtain whatever session parameters are needed
    """
    font = ("Arial", 14)
    layout = [
        [sg.Text("Participant ID", font=font), sg.Input(key="subid", default_text="0", enable_events=True, font=font)],
        [sg.Text("Session #", font=font), sg.Input(key="session", default_text="1", enable_events=True, font=font)],
        [sg.Text(" ")],
        [sg.Button("Ok", key="Ok", disabled=False, font=font), sg.Button("Quit", font=font)],
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

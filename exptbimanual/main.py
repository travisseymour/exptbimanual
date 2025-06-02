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

import platform
import sys
import threading
from types import SimpleNamespace


import pygame
from rich import print

from exptbimanual.exptsys.response import find_devices, input_thread, stop_event
from exptbimanual.version import __version__
from exptbimanual.apputils import frozen, stop_if_not_linux, set_qt_platform

from exptbimanual.task import task_schedule, task_setup

OS = platform.system()
set_qt_platform()


def main():
    print(f"Bimanual Experiment Version {__version__} | {OS=} | {frozen()=}")

    stop_if_not_linux("ExptBimanual")

    # Parameter Setup
    # ---------------
    parameters = task_setup.get_parameters()
    if not parameters:
        sys.exit()

    # setup.options is a SimpleNamespace, parameters is a dict.
    # this expression create a merged dict out of both and then re-constitutes the SimpleNamespace
    task_setup.options = SimpleNamespace(**(task_setup.options.__dict__ | parameters))
    print(task_setup.options)

    # Setup Pygame
    # ------------
    pygame.mixer.init()
    pygame.init()
    screen = pygame.display.set_mode(task_setup.options.screen_size)
    pygame.display.set_caption("")
    clock = pygame.time.Clock()

    # setup input device handling
    # ---------------------------
    # Query system for appropriate input devices
    input_threads = []
    input_devices = find_devices(
        include_keyboards=task_setup.options.keyboard_input, include_mice=task_setup.options.mouse_input
    )
    # Announce input device list
    print("Found these EV_KEY devices:")
    for dev in input_devices:
        print(f" • {dev.path}  → {dev.name}")
    # Spawn one thread per input device
    for dev in input_devices:
        t = threading.Thread(target=input_thread, args=(dev, stop_event), daemon=True)
        t.start()
        input_threads.append((t, dev))

    try:
        # hide mouse cursor, though will still track button presses if enabled in find_devices
        pygame.mouse.set_visible(False)

        # TASK PROCESSING STARTS HERE
        # =========================
        task_setup.preload_experiment_media()
        task_schedule.run(screen)

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Shutting Down.")
    finally:
        # indicate waiting state using cursor
        pygame.mouse.set_visible(True)
        wait_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_WAIT)
        pygame.mouse.set_cursor(wait_cursor)
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2
        pygame.mouse.set_pos((cx, cy))
        pygame.display.update()  # force the cursor change to appear immediately

        print("Stopping input threads...")
        stop_event.set()
        for t, dev in input_threads:
            t.join(timeout=1.0)

        # restore default mouse cursor
        arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.mouse.set_cursor(arrow_cursor)

        # shutdown pygame
        pygame.quit()
        pygame.mixer.quit()

    sys.exit()


if __name__ == "__main__":
    main()

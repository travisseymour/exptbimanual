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
from pathlib import Path

import pygame
from rich import print

from exptbimanual.propdict import PropDict
from exptbimanual.resource import get_resource
from exptbimanual.task_setup import get_parameters
from exptbimanual.version import __version__
from exptbimanual.apputils import frozen, stop_if_not_linux, set_qt_platform

OS = platform.system()
set_qt_platform()

# Set Task Options
options: PropDict = PropDict(
    {
        'bg_color': (0, 0, 0),
        'screen_size': (1024, 768),
        'practice_blocks': 1,
        'test_blocks': 1
    }
)

# Get Task Options From Experimenter


# Preload Task Media
building_files = [f'HH{i+1}BW.bmp' for i in range(6) ]
face_files = [f'FF{i+1}BW.bmp' for i in range(6) ]
media: PropDict = PropDict()

def preload_experiment_media():
    global media
    for file in building_files:
        media[Path(file).name] = pygame.image.load(get_resource('images', 'buildings', file)).convert_alpha()
    for file in face_files:
        media[Path(file).name] = pygame.image.load(get_resource('images', 'faces', file)).convert_alpha()
    media['keyboard_kl'] = pygame.image.load(get_resource('images', 'response_box', 'keyboard_as_kl.png'))
    media['keyboard_space'] = pygame.image.load(get_resource('images', 'response_box', 'keyboard_space.png'))

    print(f'Successfully preloaded media:')
    print(list(media.to_dict().keys()))

def main():
    global options
    print(f'Bimanual Experiment Version {__version__} | {OS=} | {frozen()=}')

    stop_if_not_linux('ExptBimanual')
    parameters = get_parameters()
    options = options.combine(parameters)
    print(options)


    pygame.init()
    screen = pygame.display.set_mode(options.screen_size)

    preload_experiment_media()

    # practice instructions
    # for block in num_blocks:
    #     run practice block
    #         for trial in num_trials:
    #             run_practice_trial
    #                 show stim
    #                 wait for resp
    #                 show trial feedback

    phase = ['independent', 'dependent']

    # test instructions phase[0]
    # for block in num_blocks:
    #     run test block
    #         for trial in num_trials:
    #             run_test_trial
    #                 show stim
    #                 wait for resp
    #         show block feedback

    # test instructions phase[1]
    # for block in num_blocks:
    #     run test block
    #         for trial in num_trials:
    #             run_test_trial
    #                 show stim
    #                 wait for resp
    #         show block feedback

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

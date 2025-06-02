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

import pygame

from exptbimanual.task import goodbye, practice, practice_instructions, overview_instructions


def run(screen: pygame.Surface):
    overview_instructions.run(screen)
    practice_instructions.run(screen)
    practice.run(screen)
    goodbye.run(screen)

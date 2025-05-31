from typing import Optional

import pygame
import sys


# TODO: Need to specify allowed, correct, resptype
#       option to clear key buffer?

# TODO: Later, add in that ms accuate key grabbing thread


def run_loop(
    screen: pygame.Surface,
    draw_funcs: Optional[list] = None,
    duration: int = 0,
    wait_for_key: bool = False,
    refresh_rate: int = 60,
    fill_color: str = "black",
) -> list[dict]:
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    data: list = []
    func_name = "???"
    func_start_time = pygame.time.get_ticks()

    can_continue = True
    while can_continue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if wait_for_key and event.type == pygame.KEYDOWN:
                data.append(
                    {
                        "func_name": f"{func_name}",
                        f"{func_name}_key": pygame.key.name(event.key),
                        f"{func_name}_start": func_start_time,
                        f"{func_name}_stop": pygame.time.get_ticks(),
                    }
                )
                # use can_continue when a simple break wouldn't be sufficient
                can_continue = False

        screen.fill(fill_color)  # clear screen each frame

        for func in draw_funcs:
            # assumes func returns a dict.
            func_name = func.func.__name__
            result = func()
            if result:
                data.append(result)

        pygame.display.flip()  # push the frame to the display

        if duration and pygame.time.get_ticks() - start_time >= duration:
            data.append(
                {
                    "func_name": f"{func_name}",
                    f"{func_name}_key": "",
                    f"{func_name}_start": func_start_time,
                    f"{func_name}_stop": pygame.time.get_ticks(),
                }
            )
            break

        clock.tick(refresh_rate)

    return data

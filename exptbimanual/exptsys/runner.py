from typing import Optional, List, Callable, Set

import pygame
import sys

from exptbimanual.exptsys.response import set_allowed_responses, InputRecord
import exptbimanual.exptsys.response


def run_loop(
    screen: pygame.Surface,
    display_func: Callable,
    duration: int = 0,  # will end loop if duration ms have passed
    wait_for_responses: int = 0,  # will end loop if this number of responses received. 0=don't stop on response.
    responses_allowed: Optional[List[str]] = None,  # e.g., ['A', 'SPACE', '1', '2']. If [], no restriction applied
    correct_response: str = "",  # if empty, any response is correct
    clear_inputs: bool = True,  # if True, clears response.input_events prior to running loop
    refresh_rate: int = 60,
    fill_color: str = "black",
) -> list[dict]:
    set_allowed_responses([] if not responses_allowed else responses_allowed)

    if clear_inputs:
        exptbimanual.exptsys.response.input_events.clear()

    responses: Set[InputRecord] = set()
    data: list = []
    clock = pygame.time.Clock()

    start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # clear screen each frame
        screen.fill(fill_color)

        # use display_func to draw frame contents offscreen
        result = display_func()  # should return a dict
        if result:
            data.append(result)

        # break out of loop if duration set and expired
        if duration and pygame.time.get_ticks() - start_time >= duration:
            break

        # get any existing responses available in input event queue
        for response in exptbimanual.exptsys.response.input_events.all_responses():
            # If we see our shutdown marker, bail out
            if response.value == "__EXIT__":
                running = False
                sys.exit()

            # otherwise, store the response
            responses.add(response)
            print(f"RECEIVED RESPONSE: {response}")

        # break out of loop if waiting for 1 or more responses and they have been registered
        if wait_for_responses and len(responses) >= wait_for_responses:
            break

        # push the frame to the display
        pygame.display.flip()
        clock.tick(refresh_rate)

    # store final bit of data for this loop
    end_time = pygame.time.get_ticks()
    if not correct_response:
        correct = True
    else:
        response_value_set = set(str(resp_rec.value).upper() for resp_rec in responses)
        correct = correct_response in response_value_set

    data.append(
        {
            "display_func": f"{display_func.func.__name__}",
            "loop_start": start_time,
            "stop": end_time,
            "duration": end_time - start_time,
            "responses": responses,
            "correct_resp": correct_response,
            "correct": correct,
        }
    )

    return data

from dataclasses import dataclass
from enum import StrEnum
from typing import List, Tuple


import pygame
import threading
from timeit import default_timer
from queue import Queue, Empty
from evdev import InputDevice, ecodes, list_devices
import rich


class InputSource(StrEnum):
    keyboard = "keyboard"
    mouse = "mouse"


@dataclass(frozen=True)
class InputRecord:
    type: InputSource
    device: str
    value: str
    time: float

    def __repr__(self) -> str:
        return (
            f'InputRecord(type="{self.type}", device="{self.device}", '
            f"{'key=' + str(self.value) if self.type == InputSource.keyboard else 'button=' + str(self.value)}, "
            f"time={self.time:0.3f})"
        )


class InputEvents:
    def __init__(self):
        self._responses: Queue[InputRecord] = Queue()

    def put(self, rec: InputRecord):
        self._responses.put(rec)

    def get(self) -> InputRecord:
        """
        InputEvents uses a queue.Queue as its data structure, so this .get()
        method pops (i.e., consumes) an item and returns it
        """
        return self._responses.get()

    def qsize(self) -> int:
        """
        __Approximate__, value could change during this query
        """
        return self._responses.qsize()

    def has_responses(self) -> bool:
        return not self._responses.empty()

    def all_responses(self) -> List[InputRecord]:
        """
        Remove and return a list (in arrival order) of all records currently queued.
        The returned items are removed (i.e., consumed) as they are collected.
        """
        items: List[InputRecord] = []
        while True:
            try:
                items.append(self._responses.get_nowait())
            except Empty:
                break
        return items

    def clear(self) -> None:
        """
        Remove everything currently in both keyboard and mouse queues.
        Any items added after clear() starts may still end up in the queues.
        """
        # drain queue
        while True:
            try:
                self._responses.get_nowait()
            except Empty:
                break


# === Config ===
DEBOUNCE_ENABLED = True
DEBOUNCE_INTERVAL_MS = 150
DEBUG = False

# Global filters (empty list = no filtering on that category)
# e.g. ["A", "SPACE", "T"] maps to pygame's KEY_A, KEY_SPACE, and KEY_T,
#      and ["1", "2", "3"] maps to evdev codes 272, 273, 274
allowed_responses = ["A", "SPACE", "T", "1", "2"]


def set_allowed_responses(key_names: List[str]) -> Tuple[str, ...]:
    """
    Sets globally allowed keyboard keys.
    Returns a tuple of the list that was used for info purposes only
    """
    global allowed_responses
    if not key_names:
        allowed_responses = []
    else:
        allowed_responses = list(set(str(key_name).upper().removeprefix("KEY_") for key_name in set(key_names)))
    return tuple(allowed_responses)


def print_nothing(*args, **kwargs): ...


if DEBUG:
    debug_print = rich.print
else:
    debug_print = print_nothing


input_events: InputEvents = InputEvents()
stop_event = threading.Event()


def find_devices(include_keyboards: bool = True, include_mice: bool = True):
    """
    Return a filtered list of InputDevice objects that correspond to:
      - “real” keyboards (devices with EV_KEY that include KEY_A), and
      - “real” mice (devices with EV_REL that include REL_X and REL_Y).
    Skip any device that does not satisfy one of these two roles.
    """

    raw_paths = list_devices()
    keyboards = []
    mice = []

    for path in raw_paths:
        try:
            dev = InputDevice(path)
        except Exception as e:
            # Couldn’t open (probably permissions). Skip.
            debug_print(f"[DEBUG] Could not open {path}: {e}")
            continue

        caps = dev.capabilities()
        # caps is a dict mapping ev_type → list/tuple of event codes or AbsInfo, e.g.
        #   { 0: [0,1,4],        # EV_SYN
        #     1: [1,2,3,4,5,...] # EV_KEY codes
        #     2: [0, 1, …],      # EV_REL codes
        #     3: [(32,AbsInfo …)]# EV_ABS
        #     …
        #   }

        # Check for keyboard: must have EV_KEY (ecodes.EV_KEY == 1) and KEY_A (code 30) in that list
        if ecodes.EV_KEY in caps:
            key_codes = caps[ecodes.EV_KEY]
            if 30 in key_codes:  # 30 == ecodes.KEY_A
                # This node truly behaves like an alphanumeric keyboard
                keyboards.append(dev)
                continue

        # Check for mouse: must have EV_REL (ecodes.EV_REL == 2) and REL_X, REL_Y in that list
        if ecodes.EV_REL in caps:
            rel_codes = caps[ecodes.EV_REL]
            if 0 in rel_codes and 1 in rel_codes:
                #  0 == ecodes.REL_X, 1 == ecodes.REL_Y
                mice.append(dev)
                continue

        # Otherwise, skip this device; it’s not a primary keyboard or primary mouse.
        dev.close()

    # It’s possible you have multiple physical keyboards or mice.
    # We’ll return *all* of them (e.g. two USB keyboards, etc.), so that
    # the rest of your program spawns one thread per actual keyboard and mouse.
    #
    # If you wanted only the “first” of each category, you could do:
    #     return ([keyboards[0]] if keyboards else []) + ([mice[0]] if mice else [])
    #
    # But here we assume you want to log from every connected keyboard+mouse.

    devices = []
    if include_keyboards:
        devices.extend(keyboards)
    if include_mice:
        devices.extend(mice)

    return tuple(devices)


def input_thread(dev: InputDevice, stop_event: threading.Event):
    """
    Each device thread:
      • Grabs the device (if possible)
      • Keeps track of which keys are currently pressed on this device
      • On key-down, enqueues the event (with debounce + filtering)
      • If (Ctrl) + X is detected, enqueues a special ("__EXIT__", "", 0.0) marker
        and signals stop_event so that all threads—and the main loop—shut down.
    """
    last_press_time = {}
    debounce_interval = DEBOUNCE_INTERVAL_MS / 1000.0

    # A set of currently pressed keys on this device, e.g. {"KEY_LEFTCTRL", "KEY_A", ...}
    dev.pressed_keys = set()

    # Map raw evdev button codes to “button numbers” 1,2,3
    btn_map = {
        ecodes.BTN_LEFT: "1",  # left button → 1
        ecodes.BTN_RIGHT: "2",  # right button → 2
        ecodes.BTN_MIDDLE: "3",  # middle button → 3
    }

    debug_print(f"[THREAD] Starting thread for {dev.name} ({dev.path})")
    try:
        # Attempt to grab the device; if it fails, we still proceed without crashing
        try:
            dev.grab()
            debug_print(f"[THREAD] Successfully grabbed {dev.name}")
        except Exception as e:
            debug_print(f"[THREAD] Warning: could not grab {dev.name}: {e}")

        for event in dev.read_loop():
            if stop_event.is_set():
                break

            if event.type == ecodes.EV_KEY:
                key_name = ecodes.KEY.get(event.code, f"KEY_{event.code}")
                now = default_timer()

                # --- KEY DOWN (value == 1) ---
                if event.value == 1:
                    # Mark this key/button as pressed
                    dev.pressed_keys.add(key_name)

                    # 1) Always check for Ctrl+X → shutdown (unfiltered)
                    has_ctrl = "KEY_LEFTCTRL" in dev.pressed_keys or "KEY_RIGHTCTRL" in dev.pressed_keys
                    is_x = key_name == "KEY_X"
                    if is_x and has_ctrl:
                        debug_print("[THREAD] Detected Ctrl+X → initiating shutdown.")
                        input_events.put(InputRecord(InputSource.keyboard, dev.name, "__EXIT__", 0.0))
                        stop_event.set()
                        break

                    # 2) Determine if this is a mouse-button code
                    if event.code in btn_map:
                        button_number = btn_map[event.code]
                        # If allowed_responses is empty → no filter; otherwise only that list
                        if (not allowed_responses) or (button_number in allowed_responses):
                            # We pass through the raw evdev code for the mouse button (e.g. 272/273/274)
                            input_events.put(InputRecord(InputSource.mouse, dev.name, str(event.code - 271), now))
                    else:
                        # Otherwise, assume it’s a “keyboard” key
                        # Strip off the "KEY_" prefix:
                        stripped = key_name.replace("KEY_", "", 1)
                        # If allowed_responses is empty → no filter; otherwise only that list
                        if (not allowed_responses) or (stripped in allowed_responses):
                            input_events.put(
                                InputRecord(InputSource.keyboard, dev.name, str(key_name).removeprefix("KEY_"), now)
                            )

                    # Update debounce timestamp if we enqueued anything:
                    if DEBOUNCE_ENABLED:
                        last_press_time[key_name] = now

                # --- KEY UP (value == 0) ---
                elif event.value == 0:
                    if key_name in dev.pressed_keys:
                        dev.pressed_keys.remove(key_name)

                # (We ignore event.value == 2, which is “autorepeat.”)

    except Exception as e:
        debug_print(f"[{dev.name}] Input thread crashed: {e}")

    finally:
        debug_print(f"[THREAD] Releasing and closing {dev.name}")
        try:
            dev.ungrab()
        except Exception:
            pass
        dev.close()


if __name__ == "__main__":

    def response_module_test():
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Verdana", 18)
        pygame.display.set_caption("Multi-Device Input Logger (Ctrl+X to Exit)")
        pygame.mouse.set_visible(False)

        devices = find_devices()
        debug_print("Found these EV_KEY devices:")
        for dev in devices:
            debug_print(f" • {dev.path}  → {dev.name} (caps: {dev.capabilities()})")

        threads = []
        try:
            # Spawn one thread per EV_KEY device
            for dev in devices:
                t = threading.Thread(target=input_thread, args=(dev, stop_event), daemon=True)
                t.start()
                threads.append((t, dev))

            running = True
            event_log = []

            while running:
                screen.fill((255, 255, 255))

                # Let the user still close the window with the "X" button
                for evt in pygame.event.get():
                    if evt.type == pygame.QUIT:
                        running = False

                # Drain any queued input_events
                responses = input_events.all_responses()
                for response in responses:
                    # If we see our shutdown marker, bail out
                    if response.value == "__EXIT__":
                        running = False
                        break

                    # Otherwise, this was a normal key-down event
                    debug_print(f"[MAIN] {response}")
                    event_log.append(response)

                # Draw the last five events
                for i, record in enumerate(event_log[-5:]):
                    txt = font.render(f"{record}", True, (0, 0, 0))
                    screen.blit(txt, (20, 20 + 30 * i))

                pygame.display.flip()
                clock.tick(60)

        except KeyboardInterrupt:
            debug_print("[MAIN] KeyboardInterrupt: shutting down.")

            debug_print("[MAIN] Stopping threads...")

            # unhide mouse
            pygame.mouse.set_visible(True)

            # change to a spinner/wait cursor
            wait_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_WAIT)
            pygame.mouse.set_cursor(wait_cursor)
            cx = screen.get_width() // 2
            cy = screen.get_height() // 2
            pygame.mouse.set_pos((cx, cy))
            pygame.display.update()  # force the cursor change to appear immediately

            stop_event.set()
            for t, dev in threads:
                t.join(timeout=1.0)

            # restore default mouse cursor
            arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygame.mouse.set_cursor(arrow_cursor)

            pygame.quit()
            debug_print("[MAIN] Exited cleanly.")

    response_module_test()

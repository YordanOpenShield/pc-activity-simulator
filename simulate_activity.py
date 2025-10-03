"""Simple mouse activity simulator for Windows.

Usage:
    python simulate_activity.py --interval-minutes 4

Config via config.yaml (optional)
"""
import argparse
import random
import time
import threading
import os
from contextlib import contextmanager

import activities.mouse as mouse_activity
import activities.notepad as notepad_activity

try:
    import pyautogui
except Exception:
    # don't raise here so tests can import the module and mock pyautogui
    pyautogui = None

try:
    import win32con
    import win32api
    import win32gui
    import win32process
    import win32event
    import win32timezone
    import ctypes
except Exception:
    # We'll only need win32 for the prevent-sleep helper; allow script to run without it
    win32_available = False
else:
    win32_available = True


@contextmanager
def prevent_sleep_windows(enabled: bool):
    """Prevent Windows from sleeping while context is active.

    Uses SetThreadExecutionState to request the system and display stay awake.
    If the win32 libraries aren't available, this becomes a no-op.
    """
    if not enabled or not win32_available:
        yield
        return

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED) # type: ignore
    try:
        yield
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS) # type: ignore


def run_loop(activity_type: str, interval_seconds: int, stop_event: threading.Event, max_offset=5, verbose=False):
    """Run the main loop: every interval_seconds, make a small mouse move."""
    if verbose:
        print(f"Starting activity loop: interval={interval_seconds}s, max_offset={max_offset}")
    while not stop_event.is_set():
        if activity_type == "mouse":
            mouse_activity.small_random_move(max_offset=max_offset)
        elif activity_type == "notepad":
            notepad_activity.handler()
        if verbose:
            print("Moved mouse")
        # wait, but wake up on stop_event
        stop_event.wait(interval_seconds)


def parse_args():
    parser = argparse.ArgumentParser(description="Simulate small mouse activity to prevent Teams from marking you away.")
    parser.add_argument("--interval-minutes", type=float, default=4.0, help="Interval in minutes between moves (default: 4)")
    parser.add_argument("--no-prevent-sleep", dest="prevent_sleep", action="store_false", help="Don't request Windows to stay awake")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--activity-type", choices=["mouse", "notepad"], default="mouse", help="Type of activity to simulate (default: mouse)")
    return parser.parse_args()


def main():
    args = parse_args()
    interval_seconds = max(5, int(args.interval_minutes * 60))

    stop_event = threading.Event()

    try:
        with prevent_sleep_windows(args.prevent_sleep):
            t = threading.Thread(target=run_loop, args=(args.activity_type, interval_seconds, stop_event, args.verbose), daemon=True)
            t.start()
            if args.verbose:
                print("Press Ctrl+C to exit")
            while t.is_alive():
                t.join(1)
    except KeyboardInterrupt:
        stop_event.set()
        print("Stopping...")


if __name__ == "__main__":
    main()

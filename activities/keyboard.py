"""Keyboard helpers: type random symbols and delete characters using pyautogui.

Functions:
- type_random_symbols(count, interval_between_keys, allowed_chars) -> str
- delete_symbols(count, interval_between_keys) -> None

These functions raise ImportError if pyautogui is not installed.
"""
from __future__ import annotations

import random
import string
from typing import Optional

try:
    import pyautogui
except Exception:
    pyautogui = None


def _require_pyautogui():
    if pyautogui is None:
        raise ImportError("pyautogui is required for keyboard operations. Install with: pip install pyautogui")


def type_random_symbols(count: int = 10, interval_between_keys: float = 0.02, allowed_chars: Optional[str] = None) -> str:
    """Type `count` random characters into the active window and return the actual string typed.

    - count: number of characters to type (must be >= 0)
    - interval_between_keys: delay between individual key presses
    - allowed_chars: optional string of characters to choose from; defaults to printable characters
    """
    _require_pyautogui()
    if count <= 0:
        return ""
    pool = allowed_chars or string.printable.strip()
    chars = ''.join(random.choice(pool) for _ in range(count))
    # pyautogui.write will send the characters with the given interval
    pyautogui.write(chars, interval=interval_between_keys) # type: ignore
    return chars


def delete_symbols(count: int = 10, interval_between_keys: float = 0.02) -> None:
    """Delete `count` characters from the active window by sending Backspace presses.

    - count: number of backspaces to send (must be >= 0)
    - interval_between_keys: delay between individual key presses
    """
    _require_pyautogui()
    if count <= 0:
        return
    # pyautogui.press supports presses and interval
    try:
        pyautogui.press('backspace', presses=count, interval=interval_between_keys) # type: ignore
    except TypeError:
        # older pyautogui may not support presses kwarg: fallback to loop
        for _ in range(count):
            pyautogui.press('backspace') # type: ignore
            if interval_between_keys:
                pyautogui.sleep(interval_between_keys) # type: ignore

import random
import pyautogui


def small_random_move(max_offset=5):
    """Move the mouse by a small random offset and return the new position."""
    if pyautogui is None:
        raise ImportError("pyautogui is required to move the mouse. Install with: pip install pyautogui")
    x, y = pyautogui.position()
    dx = random.randint(-max_offset, max_offset)
    dy = random.randint(-max_offset, max_offset)
    # avoid zero-length moves occasionally
    if dx == 0 and dy == 0:
        dx = 1
    new_x = x + dx
    new_y = y + dy
    pyautogui.moveTo(new_x, new_y, duration=0.1)
    return new_x, new_y
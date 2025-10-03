"""Helpers to ensure Notepad is running and to find its window handle.

Primary function: ensure_notepad(timeout=5)
- returns a tuple (hwnd, process) where hwnd is the window handle or None,
  and process is a subprocess.Popen object when we started Notepad (or None).

This module prefers pywin32 (win32gui) when available to locate and focus
Notepad windows. If pywin32 is not installed, it will still start Notepad via
subprocess but won't be able to return a window handle.
"""
from __future__ import annotations

import subprocess
import time
from typing import Optional, Tuple
import pyautogui

try:
	import win32gui
	import win32con
	win32_available = True
except Exception:
	win32_available = False
    
import activities.keyboard as keyboard_activity



def focus_notepad(hwnd: Optional[int]) -> bool:
	"""Bring Notepad window to foreground (best-effort)."""
	if hwnd is None:
		return False
	if not win32_available:
		return False
	try:
		win32gui.ShowWindow(hwnd, win32con.SW_SHOW) # type: ignore
		win32gui.SetForegroundWindow(hwnd) # type: ignore
		return True
	except Exception:
		return False


def ensure_notepad_tab(marker: str = "[Activity Simulation]", timeout: float = 5.0, create_if_missing: bool = True) -> Optional[int]:
	"""Ensure a Notepad tab containing `marker` exists and is focused.

	Returns the Notepad window handle if focused, otherwise None.

	Behaviour:
	- Ensures Notepad is running and focused.
	- Iterates open tabs by sending Ctrl+Tab and checking the window title for `marker`.
	- If found, leaves that tab active and returns hwnd.
	- If not found and create_if_missing is True, opens a new tab and performs a Save As
	  with a filename containing the marker so it will appear in the tab list next time.

	Notes: This is a best-effort approach using keyboard shortcuts. It requires pyautogui
	to be installed for sending hotkeys. The exact shortcuts (Ctrl+Tab, Ctrl+T, Ctrl+S)
	correspond to modern Notepad on Windows 11; behaviour may vary on older systems.
	"""
	# Need pyautogui for keyboard interaction
	if pyautogui is None:
		raise ImportError("pyautogui is required for tab operations. Install with: pip install pyautogui")

	hwnd, proc = ensure_notepad(timeout=timeout)
	if hwnd is None and proc is None:
		# Notepad couldn't be opened or found
		return None

	# focus Notepad
	focus_notepad(hwnd)
	time.sleep(0.15)

	seen_titles = []
	try:
		# read initial title
		if win32_available and hwnd is not None:
			title = win32gui.GetWindowText(hwnd) or '' # type: ignore
		else:
			title = ''
		seen_titles.append(title)

		# iterate tabs by sending Ctrl+Tab up to a reasonable limit
		max_tabs = 50
		for _ in range(max_tabs):
			if marker in title:
				return hwnd

			# send Ctrl+Tab to move to next tab
			pyautogui.hotkey('ctrl', 'tab')
			time.sleep(0.15)

			# read new title
			if win32_available and hwnd is not None:
				new_title = win32gui.GetWindowText(hwnd) or '' # type: ignore
			else:
				new_title = ''

			# if we cycled back to a seen title, stop
			if new_title in seen_titles:
				break
			seen_titles.append(new_title)
			title = new_title

	except Exception:
		# best-effort: if anything goes wrong, continue to create a new tab if requested
		pass

	# Not found — create new tab if requested
	if create_if_missing:
		# Try to create a new tab: Ctrl+T (Windows 11 Notepad) or fallback to Ctrl+N
		try:
			pyautogui.hotkey('ctrl', 't')
			time.sleep(0.2)
		except Exception:
			try:
				pyautogui.hotkey('ctrl', 'n')
				time.sleep(0.2)
			except Exception:
				pass
		finally:
			# Include the marker in the new tab
			try:
				pyautogui.write(marker, interval=0.01)
				pyautogui.press('enter')
				pyautogui.press('enter')
			except Exception:
				pass

		# Try to read/focus the window again
		time.sleep(0.2)
		hwnd = find_notepad_window()
		if hwnd:
			focus_notepad(hwnd)
		return hwnd

	return None


def find_notepad_window() -> Optional[int]:
	"""Return a top-level Notepad window handle if found, otherwise None.

	This searches visible top-level windows for a title or class name
	containing 'Notepad'.
	"""
	if not win32_available:
		return None

	hwnds = []

	def _enum(hwnd, extra):
		try:
			if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd): # type: ignore
				title = win32gui.GetWindowText(hwnd) or '' # type: ignore
				cls = win32gui.GetClassName(hwnd) or '' # type: ignore
				if 'Notepad' in title or 'Notepad' in cls:
					hwnds.append(hwnd)
		except Exception:
			pass

	win32gui.EnumWindows(_enum, None) # type: ignore
	return hwnds[0] if hwnds else None


def open_notepad() -> subprocess.Popen:
	"""Start Notepad and return the subprocess.Popen object."""
	return subprocess.Popen(['notepad.exe'])


def ensure_notepad(timeout: float = 5.0) -> Tuple[Optional[int], Optional[subprocess.Popen]]:
	"""Ensure Notepad is open and return (hwnd, process).

	- If Notepad is already open, returns (hwnd, None).
	- If Notepad is not open, this starts it and waits up to `timeout`
	  seconds for a window to appear. Returns (hwnd_or_None, proc).

	If pywin32 isn't available, hwnd will be None but Notepad will still
	be launched via subprocess.
	"""
	hwnd = find_notepad_window()
	proc = None
	if hwnd is not None:
		return hwnd, None

	# Not found => launch
	proc = open_notepad()

	if not win32_available:
		return None, proc

	# wait for window to appear
	end = time.time() + timeout
	while time.time() < end:
		hwnd = find_notepad_window()
		if hwnd:
			return hwnd, proc
		time.sleep(0.1)

	# timed out
	return None, proc


def close_notepad(hwnd: Optional[int] = None, proc: Optional[subprocess.Popen] = None, timeout: float = 5.0, force: bool = False) -> bool:
	"""Try to close Notepad.

	Parameters
	- hwnd: optional window handle to close. If omitted, the function will try to find a Notepad window.
	- proc: optional subprocess.Popen for a Notepad process that was started by this program.
	- timeout: seconds to wait for graceful close before considering it failed.
	- force: if True, use taskkill to forcefully terminate Notepad if graceful close fails.

	Returns True if Notepad was closed (or no Notepad found), False otherwise.
	"""
	closed = False

	# If no hwnd given, try to find one
	if hwnd is None:
		hwnd = find_notepad_window()

	# If we have a window handle and win32 is available, post WM_CLOSE
	if hwnd is not None and win32_available:
		try:
			win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0) # type: ignore
		except Exception:
			pass

		# wait for the window to disappear
		end = time.time() + timeout
		while time.time() < end:
			# if the window no longer exists, consider it closed
			found = find_notepad_window()
			if found is None or found != hwnd:
				closed = True
				break
			time.sleep(0.1)

	# If we still haven't closed and a proc object exists, try terminating it
	if not closed and proc is not None:
		try:
			if proc.poll() is None:
				proc.terminate()
				proc.wait(timeout=timeout)
			closed = True
		except Exception:
			# Try force kill if requested
			if force:
				try:
					proc.kill()
					proc.wait(timeout=2)
					closed = True
				except Exception:
					pass

	# If still not closed and force requested, fall back to taskkill
	if not closed and force:
		try:
			# taskkill may require privileges but is a last-resort attempt
			subprocess.run(['taskkill', '/f', '/im', 'notepad.exe'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			closed = True
		except Exception:
			pass

	return closed

def handler():
	"""A simple handler function."""

	hwnd, proc = ensure_notepad(timeout=5.0)
	if hwnd:
		focus_notepad(hwnd)

	hwnd = ensure_notepad_tab(marker='[Activity Simulation]', timeout=5.0, create_if_missing=True)
	if hwnd:
		focus_notepad(hwnd)

	# give focus a moment, then type
	time.sleep(0.2)
	typed = keyboard_activity.type_random_symbols(count=8, interval_between_keys=0.01)
	print('typed:', repr(typed))
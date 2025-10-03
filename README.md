# Activity Simulator (Microsoft Teams)

Small Python utility to simulate mouse activity on Windows to keep apps like Microsoft Teams from marking you as away.

Features
- Move the mouse by a small random offset at a configurable interval
- Optional Windows "prevent sleep" while the script runs
- Configurable via CLI flags
- Includes a lightweight unit test for core logic

Requirements
- Windows (script uses a Windows API call to optionally prevent sleep)
- Python 3.8+

Usage

```powershell
ActivitySimulator.exe --activity-type=notepad --verbose --interval-minutes=1
```

Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python simulate_activity.py --activity-type=notepad --verbose --interval-minutes=1
```

To run automatically, schedule this script with Windows Task Scheduler to run at login.

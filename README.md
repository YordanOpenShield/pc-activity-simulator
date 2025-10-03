# Activity Simulator (Microsoft Teams)

Small Python utility to simulate mouse activity on Windows to keep apps like Microsoft Teams from marking you as away.

Features
- Move the mouse by a small random offset at a configurable interval
- Optional Windows "prevent sleep" while the script runs
- Configurable via `config.yaml` or CLI flags
- Includes a lightweight unit test for core logic

Requirements
- Windows (script uses a Windows API call to optionally prevent sleep)
- Python 3.8+

Installation
1. Open PowerShell and create a venv (recommended):

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Running

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
python simulate_activity.py --interval-minutes 1
```

To run automatically, schedule this script with Windows Task Scheduler to run at login.

Notes
- The script uses tiny mouse moves (few pixels) so it won't interrupt work.
- Use responsibly and ensure it complies with your organization's policies.

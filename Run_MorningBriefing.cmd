@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0morning_briefing.ps1" -RefreshStripe -TrimRamIfHigh
pause

@echo off
REM Weekly Event Data Refresh - Windows Batch Script
REM This file makes it easy to run the update script and can be scheduled in Task Scheduler

echo ========================================
echo Story Time Locator - Weekly Refresh
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python update script
python update_events.py

REM Pause so you can see the results (remove this line when scheduling)
pause

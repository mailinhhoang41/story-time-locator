@echo off
REM Windows Batch Script to Update Story Time Events
REM Double-click this file to refresh all event data!

echo ========================================
echo  Story Time Locator - Update Events
echo ========================================
echo.

python update_all_events.py

echo.
echo Press any key to close...
pause > nul

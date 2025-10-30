@echo off
REM ONE-CLICK UPDATE AND DEPLOY
REM This updates BOTH local and live site

echo ================================================
echo  Story Time Locator - Update and Deploy
echo ================================================
echo.
echo This will:
echo   1. Fetch fresh data from all sources
echo   2. Update your local files
echo   3. Push to GitHub
echo   4. Deploy to live site (3-5 min)
echo.
echo ================================================
echo.

python update_and_deploy.py

echo.
echo Press any key to close...
pause > nul

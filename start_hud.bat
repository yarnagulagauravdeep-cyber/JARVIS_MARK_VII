@echo off
title J.A.R.V.I.S Mark VII - Executive HUD
echo ========================================================
echo   Starting J.A.R.V.I.S Mark VII Server...
echo ========================================================
echo.

:: Clean up any orphan server processes and cache
taskkill /f /im python.exe >nul 2>&1
if exist __pycache__ rd /s /q __pycache__ >nul 2>&1

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Start server in background
start /b python jarvis_server.py

:: Give server 2 seconds to bind port 8000
timeout /t 2 /nobreak >nul

:: Open browser with unique fresh URL to bypass any stale browser cache
start http://localhost:8000/?fresh=%random%

echo.
echo ========================================================
echo   J.A.R.V.I.S is LIVE and running on http://localhost:8000
echo   - Click anywhere on the browser screen to engage voice.
echo   - Just speak aloud naturally anytime.
echo   - Press any key in this window to stop Jarvis.
echo ========================================================
echo.

pause >nul
taskkill /f /im python.exe >nul 2>&1

@echo off
title J.A.R.V.I.S Mark VII - Server Engine
echo ========================================================
echo   J.A.R.V.I.S Mark VII - Initializing System...
echo ========================================================
echo.

:: Clear Python cache
if exist __pycache__ rd /s /q __pycache__ >nul 2>&1

:: Activate virtual environment if valid
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

:: Free port 8000 if occupied by a previous process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Launch browser in 2 seconds in background
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; $rnd = Get-Random; Start-Process 'http://127.0.0.1:8000/?fresh=' + $rnd"

echo ========================================================
echo   J.A.R.V.I.S Server is running on http://127.0.0.1:8000
echo   - Keep this window open while using Jarvis
echo   - Close this window or press Ctrl+C to stop Jarvis
echo ========================================================
echo.

python jarvis_server.py

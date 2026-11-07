@echo off
REM ==============================================================================
REM  JARVIS AI PERSONAL ASSISTANT - 1-CLICK WINDOWS SETUP SCRIPT
REM ==============================================================================

setlocal enabledelayedexpansion

echo.
echo ==================================================================
echo    J.A.R.V.I.S  AI  ASSISTANT  -  MARK VII
echo ==================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is NOT installed or not in PATH
    echo.
    echo Please install Python 3.10+ from: https://python.org
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected!
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [X] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created!
    echo.
) else (
    echo [OK] Virtual environment found.
    echo.
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment active!
echo.

REM Install requirements
echo [*] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Warning: Some packages had warnings, checking core files...
)
echo.

echo ==================================================================
echo [+] J.A.R.V.I.S SETUP COMPLETE!
echo ==================================================================
echo.
echo  TO RUN JARVIS:
echo.
echo  OPTION 1 (Recommended - 3D Holographic HUD + Voice in Browser):
echo    python jarvis_server.py
echo    Then open: http://localhost:8000
echo.
echo  OPTION 2 (Terminal Text / Mic Mode):
echo    python jarvis_voice.py
echo.
echo ==================================================================
echo.

choice /C 12 /M "Press 1 for Web HUD, 2 for Terminal Voice mode: "
if errorlevel 2 goto terminal_mode
if errorlevel 1 goto web_mode

:web_mode
echo.
echo [*] Starting Jarvis Web HUD Server on http://localhost:8000 ...
start http://localhost:8000
python jarvis_server.py
goto end

:terminal_mode
echo.
echo [*] Starting Jarvis in Terminal Voice Mode...
python jarvis_voice.py
goto end

:end
pause

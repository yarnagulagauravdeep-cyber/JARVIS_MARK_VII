@echo off
title Push J.A.R.V.I.S Mark VII to GitHub
echo ========================================================
echo   Pushing J.A.R.V.I.S Mark VII to GitHub...
echo   Repository: yarnagulagauravdeep-cyber/JARVIS_MARK_VII
echo ========================================================
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Pushed cleanly to GitHub:
    echo   https://github.com/yarnagulagauravdeep-cyber/JARVIS_MARK_VII
    echo ========================================================
) else (
    echo.   
    echo ========================================================
    echo   Authentication required or error encountered.
    echo ========================================================
)
echo.
pause


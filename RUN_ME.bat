@echo off
setlocal
cd /d "%~dp0"
title Divya Jain Portfolio

set "PORTFOLIO_PYTHON=.venv\Scripts\python.exe"

if not exist "%PORTFOLIO_PYTHON%" (
    echo [Setup] Creating the Python virtual environment...

    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        where python >nul 2>nul
        if errorlevel 1 goto :python_missing
        python -m venv .venv
    )

    if errorlevel 1 goto :setup_failed
)

"%PORTFOLIO_PYTHON%" -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo [Setup] Installing required packages...
    "%PORTFOLIO_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 goto :setup_failed
)

echo.
echo Portfolio is starting at http://127.0.0.1:5000
echo Keep this window open. Press Ctrl+C to stop the server.
echo.

if /I not "%~1"=="--no-browser" (
    start "" powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:5000'"
)

"%PORTFOLIO_PYTHON%" app.py
set "PORTFOLIO_EXIT_CODE=%ERRORLEVEL%"

if not "%PORTFOLIO_EXIT_CODE%"=="0" (
    echo.
    echo The portfolio stopped because of an error.
    pause
)

exit /b %PORTFOLIO_EXIT_CODE%

:python_missing
echo.
echo Python 3.11 or newer is required but was not found.
echo Install Python from https://www.python.org/downloads/ and run this file again.
pause
exit /b 1

:setup_failed
echo.
echo Setup failed. Check your internet connection and the error shown above.
pause
exit /b 1

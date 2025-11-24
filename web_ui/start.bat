@echo off
REM Simple startup script for DeGPT Web UI
REM This script avoids encoding issues

python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Python not found. Please install Python first.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo Starting DeGPT Web UI...
echo.
echo Please visit http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo.

%PYTHON% app.py

pause




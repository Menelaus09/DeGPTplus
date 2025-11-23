@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo DeGPT Web UI Startup Script
echo ========================================
echo.

REM Try to find Python
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :found_python
)

echo [ERROR] Python not found. Please try:
echo   1. Make sure Python is installed and added to PATH
echo   2. Or run directly: python app.py
echo   3. Or run: py app.py
echo.
pause
exit /b 1

:found_python
echo [INFO] Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo [INFO] Checking dependencies...
%PYTHON_CMD% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Flask not installed, installing dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo [TIP] Please run manually: %PYTHON_CMD% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [INFO] Starting Web server...
echo [INFO] Please visit: http://localhost:5000
echo [INFO] Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% app.py

pause

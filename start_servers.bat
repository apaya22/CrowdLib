@echo off
REM Disclosure: This script was AI Generated
REM CrowdLib Master Start Server Script for Windows
REM Automatically launches frontend and backend servers in separate terminal windows
REM Usage: start_servers.bat

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Colors and formatting
cls
echo.
echo ========================================
echo   CrowdLib Master Start Server Script
echo   Starting Frontend and Backend Servers
echo ========================================
echo.

REM Check if backend run_server.sh exists
if not exist "%SCRIPT_DIR%backend\run_server.sh" (
    echo Error: Backend run_server.sh not found
    echo Expected location: %SCRIPT_DIR%backend\run_server.sh
    pause
    exit /b 1
)
echo + Found backend run_server.sh

REM Check if frontend exists
if not exist "%SCRIPT_DIR%frontend" (
    echo Error: Frontend directory not found at %SCRIPT_DIR%frontend
    pause
    exit /b 1
)
if not exist "%SCRIPT_DIR%frontend\package.json" (
    echo Error: package.json not found in frontend directory
    pause
    exit /b 1
)
echo + Found frontend directory

REM Check if frontend dependencies are installed
if not exist "%SCRIPT_DIR%frontend\node_modules" (
    echo Error: Frontend dependencies not installed.
    echo Please run: npm install (in frontend directory) or init.bat
    pause
    exit /b 1
)
echo + Frontend dependencies are installed

REM Check if backend virtual environment exists
if not exist "%SCRIPT_DIR%backend\venv" (
    if not exist "%SCRIPT_DIR%backend\.venv" (
        echo Error: Backend virtual environment not found.
        echo Please run: init.bat
        pause
        exit /b 1
    )
)
echo + Backend virtual environment found

echo.
echo All checks passed! Starting servers...
echo.

REM Start backend server in a new terminal window
echo + Opening backend server in new window...
start cmd /k "cd /d "%SCRIPT_DIR%backend" && bash run_server.sh"

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend server in a new terminal window
echo + Opening frontend server in new window...
start cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev"

echo.
echo ========================================
echo Servers Started Successfully!
echo ========================================
echo.
echo Backend Server:  http://localhost:8000
echo Frontend Server: http://localhost:5173
echo.
echo To stop the servers, close the terminal windows or press Ctrl+C in each
echo.
pause

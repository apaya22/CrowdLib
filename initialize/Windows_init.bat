@echo off
REM CrowdLib Project Initialization Script for Windows
REM This script sets up the development environment for the CrowdLib project (Django + React)
REM Run this script after cloning the repository in Command Prompt or PowerShell

setlocal enabledelayedexpansion

REM Colors and formatting (Windows doesn't support ANSI colors easily, so we'll use simple text)
cls
echo.
echo ========================================
echo   CrowdLib Project Initialization
echo   Django + React Development Setup
echo ========================================
echo.

REM Check if required commands are available
echo Checking prerequisites...

where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH.
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo Error: npm is not installed or not in PATH.
    echo npm comes with Node.js installation.
    pause
    exit /b 1
)

echo + Python found:
python --version

echo + Node.js found:
node --version

echo + npm found:
npm --version

echo.
echo ========================================
echo Setting up Backend (Django)
echo ========================================
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Install Python dependencies
echo Installing Python dependencies from requirements.txt...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo Python dependencies installed.
) else (
    echo Error: requirements.txt not found in backend directory
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found in backend directory
    echo Please create a .env file with the required environment variables.
    echo You can use .env.example as a template.
) else (
    echo .env file found.
)

REM Run Django migrations
echo Running Django migrations...
python manage.py migrate --noinput 2>nul
if errorlevel 1 (
    echo Warning: Could not run migrations. This may be normal if database is not yet set up.
)

echo.
echo Backend setup complete!
echo.

cd ..

REM Setup Frontend
echo ========================================
echo Setting up Frontend (React)
echo ========================================
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    echo Node.js dependencies installed.
) else (
    echo Node.js dependencies already exist.
    echo Running npm install to ensure packages are up to date...
    npm install
)

echo.
echo Frontend setup complete!
echo.

cd ..

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start developing:
echo.
echo 1. Backend (Django) - Open a new Command Prompt:
echo    cd backend
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 2. Frontend (React) - Open another Command Prompt:
echo    cd frontend
echo    npm run dev
echo.
echo Important:
echo - Make sure you have a valid .env file in the backend directory
echo - The database must be accessible for Django migrations to work
echo - Frontend will typically run on http://localhost:5173
echo - Backend will typically run on http://localhost:8000
echo.
echo For more detailed setup instructions, see SETUP_GUIDE.md
echo.
pause

@echo off
REM Quick Start Script for Sign Language Translator Backend

echo ========================================
echo Sign Language Translator - Quick Start
echo ========================================
echo.

REM Check if in backend directory
if not exist "app\main.py" (
    echo ERROR: Please run this script from the backend directory!
    pause
    exit /b 1
)

echo [1/4] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
)
echo.

echo [3/4] Checking environment variables...
if not defined OPENAI_API_KEY (
    echo WARNING: OPENAI_API_KEY not set!
    echo Please set it with: set OPENAI_API_KEY=your_key_here
    echo.
    echo Continue anyway? (y/n^)
    set /p continue=
    if /i not "%continue%"=="y" exit /b 1
)
echo.

echo [4/4] Starting FastAPI server...
echo.
echo ========================================
echo Server will start on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Press CTRL+C to stop
echo ========================================
echo.

python start.py

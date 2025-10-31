@echo off
REM Start Backend and Frontend Separately

echo ========================================
echo Starting Sign Language Translator
echo ========================================
echo.

echo [Backend] Starting on http://localhost:8000
echo [Frontend] Will start on http://localhost:3000
echo.

REM Check if we're in the project root
if not exist "backend" (
    echo ERROR: Please run this from the project root directory!
    pause
    exit /b 1
)

REM Start backend in new window
echo Starting backend server...
start "Backend API" cmd /k "cd backend && python start.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo Starting frontend server...
start "Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ========================================
echo ✅ Both servers started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open frontend in browser...
pause > nul

start http://localhost:3000/templates/index.html

echo.
echo To stop servers, close the terminal windows.
echo.

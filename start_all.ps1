# PowerShell Script to Start Both Frontend and Backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Sign Language Translator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "ERROR: Please run this from the project root directory!" -ForegroundColor Red
    exit 1
}

Write-Host "[Backend] Starting on http://localhost:8000" -ForegroundColor Yellow
Write-Host "[Frontend] Starting on http://localhost:3000" -ForegroundColor Yellow
Write-Host ""

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python start.py"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python -m http.server 3000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Both servers started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening frontend in browser..." -ForegroundColor Yellow

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000/templates/index.html"

Write-Host ""
Write-Host "To stop servers, close the PowerShell windows." -ForegroundColor Yellow
Write-Host ""

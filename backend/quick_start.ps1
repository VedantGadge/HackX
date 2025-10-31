# PowerShell Quick Start Script
# Run with: .\quick_start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sign Language Translator - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in backend directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "ERROR: Please run this script from the backend directory!" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host ""

Write-Host "[3/4] Checking environment variables..." -ForegroundColor Yellow
if (-not $env:OPENAI_API_KEY) {
    Write-Host "WARNING: OPENAI_API_KEY not set!" -ForegroundColor Yellow
    Write-Host "Please set it with: `$env:OPENAI_API_KEY = 'your_key_here'" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
}
Write-Host ""

Write-Host "[4/4] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Press CTRL+C to stop" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

python start.py

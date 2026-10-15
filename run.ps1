# ============================================================================
# AgriSense-AI: Local Development Startup Script (PowerShell)
# Launches FastAPI Backend on port 8000 and Frontend HTTP Server on port 3000
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Green
Write-Host "  Starting AgriSense-AI (Tamil Nadu Paddy Decision Support Platform)" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green

# Check Python availability
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Using $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Error "[ERROR] Python is not installed or not in PATH."
    exit 1
}

$backendPath = Join-Path $PSScriptRoot "backend"
$frontendPath = Join-Path $PSScriptRoot "frontend"

Write-Host "[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

Write-Host "[2/2] Launching Frontend Server on http://127.0.0.1:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; python -m http.server 3000"

Write-Host "`n============================================================================" -ForegroundColor Green
Write-Host "  AgriSense-AI services are running:" -ForegroundColor Green
Write-Host "  - Frontend:    http://127.0.0.1:3000" -ForegroundColor White
Write-Host "  - Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  - API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Green

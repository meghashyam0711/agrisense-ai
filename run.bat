@echo off
REM ============================================================================
REM AgriSense-AI: Local Development Startup Script (Windows Command Prompt)
REM Launches FastAPI Backend on port 8000 and Frontend HTTP Server on port 3000
REM ============================================================================

echo ============================================================================
echo   Starting AgriSense-AI (Tamil Nadu Paddy Decision Support Platform)
echo ============================================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "AgriSense Backend (FastAPI)" cmd /k "cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Launching Frontend Server on http://127.0.0.1:3000 ...
start "AgriSense Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ============================================================================
echo   AgriSense-AI services are running:
echo   - Frontend:    http://127.0.0.1:3000
echo   - Backend API: http://127.0.0.1:8000
echo   - API Docs:    http://127.0.0.1:8000/docs
echo ============================================================================
echo Close the launched command windows to stop services.

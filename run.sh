#!/usr/bin/env bash
# ============================================================================
# AgriSense-AI: Local Development Startup Script (Bash)
# Launches FastAPI Backend on port 8000 and Frontend HTTP Server on port 3000
# ============================================================================

set -e

echo "============================================================================"
echo "  Starting AgriSense-AI (Tamil Nadu Paddy Decision Support Platform)"
echo "============================================================================"

# Navigate to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..."
(cd backend && $PYTHON_CMD -m uvicorn main:app --reload --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

echo "[2/2] Starting Frontend on http://127.0.0.1:3000 ..."
(cd frontend && $PYTHON_CMD -m http.server 3000) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM EXIT

echo ""
echo "============================================================================"
echo "  AgriSense-AI services are running (Press Ctrl+C to stop):"
echo "  - Frontend:    http://127.0.0.1:3000"
echo "  - Backend API: http://127.0.0.1:8000"
echo "  - API Docs:    http://127.0.0.1:8000/docs"
echo "============================================================================"

wait

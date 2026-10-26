#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "🚀 Starting Smart Estate AI Platform"
echo "=================================================="

# Check and free port 8000 if occupied
if lsof -ti :8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is occupied. Clearing port 8000..."
    kill -9 $(lsof -ti :8000) 2>/dev/null || true
    sleep 1
fi

# Cleanup handler to stop backend when frontend exits
cleanup() {
    echo ""
    echo "🛑 Shutting down Smart Estate AI..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Start FastAPI backend
echo "▶ Starting FastAPI Backend (http://127.0.0.1:8000)..."
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Wait briefly for backend to initialize
sleep 2

# Start Vite React Frontend
echo "▶ Starting React Frontend (http://127.0.0.1:5173)..."
cd "$DIR/frontend"
npm run dev -- --host 127.0.0.1 --port 5173

#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=========================================================="
echo "🚀 Building Smart Estate AI for Production (Render)"
echo "=========================================================="

# 1. Install Python dependencies
echo "🐍 [1/2] Installing Python ML backend dependencies..."
PYTHON_BIN=$(command -v python3 || command -v python)
$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install -r requirements.txt

# 2. Build Vite React frontend
echo "⚛️ [2/2] Building Vite React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "=========================================================="
echo "✅ Build completed successfully! Production ready."
echo "=========================================================="

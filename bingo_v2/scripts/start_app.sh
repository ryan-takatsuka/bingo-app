#!/bin/bash
# Script to start both backend and frontend for Bingo App V2

echo "Starting Bingo App V2..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Start backend in background
echo "Starting backend on port 5001..."
cd "$PROJECT_DIR/backend"

# Source conda
source ~/miniforge3/etc/profile.d/conda.sh
conda activate bingo-app

export FLASK_APP=app.py
flask run --port=5001 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend on port 3001..."
cd "$PROJECT_DIR/frontend"
PORT=3001 npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap to cleanup on script exit
trap cleanup INT TERM

echo ""
echo "Bingo App V2 is running!"
echo "Frontend: http://localhost:3001"
echo "Backend API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
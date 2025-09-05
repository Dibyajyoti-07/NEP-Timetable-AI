#!/bin/bash
# Script to start the AI Timetable Backend

echo "🚀 Starting AI Timetable Backend..."
cd backend
echo "📁 Changed to backend directory"

# Activate virtual environment
if [ -f "activate.ps1" ]; then
    echo "🔧 Activating Python environment..."
    ./activate.ps1
fi

echo "🌐 Starting FastAPI server..."
echo "📊 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 API will be running at: http://localhost:8000"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

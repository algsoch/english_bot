#!/bin/bash

# Quick start script for backend
# Run this after setup.sh

echo "🚀 Starting AI Speaking Partner Backend..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Start FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
python run.py

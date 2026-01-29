#!/bin/bash

# Quick start script for frontend
# Run this in a separate terminal

echo "🚀 Starting AI Speaking Partner Frontend..."

cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies first..."
    npm install
fi

echo "🌐 Starting Vite dev server on http://localhost:5173"
npm run dev

#!/bin/bash
# Quick start script for RAGScore web application

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your DASHSCOPE_API_KEY"
    echo "Then run this script again."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the web server
echo "🚀 Starting RAGScore web application..."
echo "📱 Open your browser to: http://localhost:8000"
echo ""
export PYTHONPATH=/home/ubuntu/RAGScore/src/ragscore
nohup python -m ragscore.web.app > app.log 2>&1 &
echo "App running with nohup. Logs: app.log"

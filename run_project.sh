#!/bin/bash

echo "Starting 3D Model Generation Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
echo "Once running, open frontend/index.html in your web browser."
uvicorn main:app --reload


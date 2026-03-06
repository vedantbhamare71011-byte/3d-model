@echo off
title 3D Model Backend Starter
cd /d "%~dp0"

echo ==========================================
echo    3D Model Website - Backend Starter
echo ==========================================
echo.

echo [1/2] Checking/Installing Python dependencies...
python -m pip install fastapi uvicorn python-multipart opencv-python numpy

echo.
echo [2/2] Starting local server at http://127.0.0.1:8000...
echo (Keep this window open while using the website!)
echo.

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The server failed to start. 
    echo Please ensure Python is installed and added to your PATH.
)

pause

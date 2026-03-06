# 3D Model Generation Web App

This is a full-stack web application designed to take multiple 360-degree panorama images and prepare them for 3D reconstruction using the `tttLRM` architecture. The website includes feature-matching visualization using OpenCV SIFT to demonstrate how 3D scenes are formed based on image similarities.

## Features
- **Modern Drag & Drop UI**: High-end styling with glassmorphism to handle multiple image uploads.
- **SIFT Feature Matching**: Python FastAPI backend matches consecutive images to visualize similarities between views, essential for COLMAP pose estimation.
- **tttLRM Integration**: The uploaded images format is converted into a structure natively recognized by the `tttLRM` model.

## Setup Instructions

Make sure you have `python` (preferably Python 3.10+) installed.

1. Install dependencies and start the backend:
    ```bash
    ./run_project.sh
    ```
2. Open the frontend:
    Once the FastAPI server is running (usually on `http://localhost:8000`), open `frontend/index.html` in your web browser.

## Note on Hardware
The final `tttLRM` 3D reconstruction pipeline strictly requires NVIDIA GPUs / CUDA and FlashAttention. Mac OS CPU/M1 architectures cannot run the final PyTorch inference out-of-the-box. The frontend successfully mocks the final generation step for demonstration purposes.

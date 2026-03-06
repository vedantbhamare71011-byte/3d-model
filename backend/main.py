import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import pipeline

app = FastAPI(title="3D Model Generation API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workspace"))
UPLOAD_DIR = os.path.join(WORKSPACE_DIR, "uploads")
MATCHES_DIR = os.path.join(WORKSPACE_DIR, "matches")
COLMAP_DIR = os.path.join(WORKSPACE_DIR, "colmap_scene")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MATCHES_DIR, exist_ok=True)
os.makedirs(COLMAP_DIR, exist_ok=True)

# Mount the static files directory to serve the matched images
app.mount("/matches", StaticFiles(directory=MATCHES_DIR), name="matches")

class UploadResponse(BaseModel):
    message: str
    match_images: List[str]

@app.post("/upload", response_model=UploadResponse)
async def upload_images(files: List[UploadFile] = File(...)):
    # Clear previous uploads to keep workspace clean
    for item in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, item))
    for item in os.listdir(MATCHES_DIR):
        os.remove(os.path.join(MATCHES_DIR, item))

    saved_files = []
    
    # Save uploaded files
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)
        
    print(f"Saved {len(saved_files)} images to {UPLOAD_DIR}")
    
    # Run feature matching pipeline to find similarities
    match_images_filenames = pipeline.process_images_for_matching(saved_files, MATCHES_DIR)
    
    # Prepare files for tttLRM COLMAP format conversion
    pipeline.prepare_colmap_structure(UPLOAD_DIR, COLMAP_DIR)
    
    return UploadResponse(
        message="Images successfully uploaded and processed. Data structured for tttLRM.",
        match_images=[f"/matches/{f}" for f in match_images_filenames]
    )

@app.post("/generate-3d")
async def generate_3d_model():
    # Mocking the 3D generation step
    # On a Windows/Linux machine with CUDA, this would trigger the actual inference script
    import asyncio
    await asyncio.sleep(2) # simulate some work
    
    # Generate mock 3D data for the visualizer
    import random
    import math
    
    # Check number of images in UPLOAD_DIR
    try:
        num_images = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
    except Exception:
        num_images = 5
        
    if num_images == 0:
        num_images = 5

    points = []
    # Create 3000 points forming a rough room/structure
    for _ in range(3000):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(2, 6)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi) + (num_images * 0.5)
        color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]
        points.append({"x": x, "y": y, "z": z, "color": color})
        
    cameras = []
    # Simulate camera poses along the Z axis 
    for i in range(num_images):
        cameras.append({
            "position": [math.sin(i)*2, math.cos(i)*2, i * 1.5],
            "quaternion": [0, 0, 0, 1]  # x, y, z, w
        })

    return {
        "status": "success",
        "message": "3D Data generated dynamically!",
        "data": {
            "points": points,
            "cameras": cameras
        }
    }

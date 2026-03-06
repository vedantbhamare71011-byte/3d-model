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
    
    return {
        "status": "success",
        "message": "3D Model generation prepared! (Note: Actual tttLRM inference requires NVIDIA CUDA on Linux/Windows. Running mock success for macOS)."
    }

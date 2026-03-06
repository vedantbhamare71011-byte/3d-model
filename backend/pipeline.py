import os
import cv2
import numpy as np

def process_images_for_matching(image_files: list[str], output_dir: str) -> list[str]:
    """
    Process a list of image file paths by performing feature matching between consecutive images.
    Returns a list of file paths to the generated match images.
    """
    if len(image_files) < 2:
        return []

    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    
    # Initialize Brute Force Matcher
    bf = cv2.BFMatcher()
    
    match_images = []

    # Sort files to ensure sequential matching works if named sequentially
    image_files.sort()

    for i in range(len(image_files) - 1):
        img1_path = image_files[i]
        img2_path = image_files[i+1]
        
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1 is None or img2 is None:
            continue
            
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Find keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)
        
        if des1 is None or des2 is None:
            continue
            
        # Match descriptors using KNN
        matches = bf.knnMatch(des1, des2, k=2)
        
        # Apply ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append([m])
                
        # Draw top matches
        # We draw the first 50 good matches to avoid clutter
        match_img = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good_matches[:50], None, 
                                       flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        out_filename = f"match_{i}_{i+1}.jpg"
        out_path = os.path.join(output_dir, out_filename)
        cv2.imwrite(out_path, match_img)
        match_images.append(out_filename)
        
    return match_images

def prepare_colmap_structure(image_dir: str, workspace_dir: str):
    """
    Mocks the process of creating the expected COLMAP structure 
    and preparing inference commands for tttLRM.
    """
    # Create required directories
    sparse_dir = os.path.join(workspace_dir, "sparse", "0")
    images_dest_dir = os.path.join(workspace_dir, "images")
    
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(images_dest_dir, exist_ok=True)
    
    # In a real scenario, COLMAP would be run here to generate cameras.bin, images.bin, etc in sparse_dir.
    # We will simulate the metadata creation that tttLRM's colmap_format_convert.py expects.
    # We create dummy cameras.txt and images.txt files.
    
    with open(os.path.join(sparse_dir, "cameras.txt"), "w") as f:
        f.write("# Camera list with one line of data per camera:\n")
        f.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
        f.write("1 PINHOLE 800 600 800 800 400 300\n")
        
    with open(os.path.join(sparse_dir, "images.txt"), "w") as f:
        f.write("# Image list with two lines of data per image:\n")
        f.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n")
        f.write("#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
        
        # Link uploaded images
        images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for i, img_name in enumerate(sorted(images)):
            image_id = i + 1
            # Mock pose
            f.write(f"{image_id} 1.0 0.0 0.0 0.0 0.0 0.0 {i*1.0} 1 {img_name}\n")
            f.write("\n")
            
            # Symlink or copy to images_dest_dir
            src_path = os.path.join(image_dir, img_name)
            dest_path = os.path.join(images_dest_dir, img_name)
            if not os.path.exists(dest_path):
                import shutil
                shutil.copy2(src_path, dest_path)

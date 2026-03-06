document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const selectedFilesDiv = document.getElementById('selected-files');
    const uploadBtn = document.getElementById('upload-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const uploadSection = document.querySelector('.upload-section');
    const resultsSection = document.getElementById('results-section');
    const matchesGrid = document.getElementById('matches-grid');
    const generate3DBtn = document.getElementById('generate-3d-btn');
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close-btn');
    const successCheck = document.getElementById('success-check');

    let currentFiles = [];

    // Backend URL (Assuming FastAPI is running on port 8000)
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Browse Button
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    // Process Files
    function handleFiles(files) {
        const newFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
        if(newFiles.length === 0) return;

        currentFiles = [...currentFiles, ...newFiles];
        updateFileDisplay();
        
        if (currentFiles.length >= 2) {
            uploadBtn.disabled = false;
            uploadBtn.classList.remove('disabled');
        }
    }

    function updateFileDisplay() {
        selectedFilesDiv.innerHTML = '';
        currentFiles.forEach((file, index) => {
            const badge = document.createElement('div');
            badge.className = 'file-badge';
            badge.innerHTML = `
                <i class="fa-solid fa-image"></i>
                <span style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${file.name}</span>
                <i class="fa-solid fa-xmark remove-file" data-index="${index}" style="cursor:pointer; margin-left:5px;"></i>
            `;
            selectedFilesDiv.appendChild(badge);
        });

        // Add remove handlers
        document.querySelectorAll('.remove-file').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-index'));
                currentFiles.splice(idx, 1);
                updateFileDisplay();
                if (currentFiles.length < 2) {
                    uploadBtn.disabled = true;
                    uploadBtn.classList.add('disabled');
                }
            });
        });
    }

    // Upload & Process
    uploadBtn.addEventListener('click', async () => {
        if (currentFiles.length < 2) return;

        loadingOverlay.classList.remove('hidden');
        
        const formData = new FormData();
        currentFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            
            // Render matches
            renderMatches(data.match_images);
            
            // Switch views
            loadingOverlay.classList.add('hidden');
            uploadSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');

            // Force container to resize appropriately
            document.querySelector('.container').style.maxWidth = '1000px';

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to process images. Is the backend running?');
            loadingOverlay.classList.add('hidden');
        }
    });

    function renderMatches(imageUrls) {
        matchesGrid.innerHTML = '';
        imageUrls.forEach(url => {
            const card = document.createElement('div');
            card.className = 'match-card';
            
            const img = document.createElement('img');
            // Prevent caching issues by adding a random query parameter
            img.src = `${API_BASE_URL}${url}?t=${new Date().getTime()}`;
            img.alt = 'Feature Match';
            
            card.appendChild(img);
            matchesGrid.appendChild(card);
        });
    }

    // Generate 3D Model
    generate3DBtn.addEventListener('click', async () => {
        generate3DBtn.innerHTML = '<div class="spinner" style="width:20px; height:20px; border-width:2px; display:inline-block; margin:0 10px -5px 0;"></div> Preparing Model...';
        generate3DBtn.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/generate-3d`, {
                method: 'POST'
            });
            const data = await response.json();
            
            modal.classList.remove('hidden');
            successCheck.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to backend.');
        } finally {
            generate3DBtn.innerHTML = '<i class="fa-solid fa-vr-cardboard"></i> Generate 3D Model with tttLRM';
            generate3DBtn.disabled = false;
        }
    });

    // Close Modal
    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

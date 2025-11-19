// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

// File upload functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultArea = document.getElementById('resultArea');
const loadingOverlay = document.getElementById('loadingOverlay');

let selectedFile = null;

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#4CAF50';
    uploadArea.style.backgroundColor = '#f0fff0';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#e0e0e0';
    uploadArea.style.backgroundColor = '#ffffff';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#e0e0e0';
    uploadArea.style.backgroundColor = '#ffffff';
    
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        uploadArea.innerHTML = `
            <img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 200px; border-radius: 8px; margin-bottom: 1rem;">
            <p>Click to change image</p>
        `;
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// Analyze image
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    loadingOverlay.style.display = 'flex';
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showResults(result);
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
    } catch (error) {
        resultArea.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        loadingOverlay.style.display = 'none';
    }
});

function showResults(result) {
    const urgencyClass = result.advice.urgency === 'high' ? 'urgent' : 
                        result.advice.urgency === 'medium' ? 'warning' : 'success';
    
    resultArea.innerHTML = `
        <div class="result-header ${urgencyClass}">
            <h3><i class="fas fa-diagnoses"></i> Diagnosis Result</h3>
            <span class="confidence">${(result.confidence * 100).toFixed(1)}% confident</span>
        </div>
        
        <div class="result-content">
            <div class="result-image">
                <img src="${result.image_url}" alt="Analyzed plant">
            </div>
            
            <div class="result-details">
                <h4>${result.disease}</h4>
                
                <div class="treatment-advice">
                    <h5><i class="fas fa-first-aid"></i> Recommended Treatment:</h5>
                    <ul>
                        ${result.advice.steps ? result.advice.steps.map(step => 
                            `<li>${step}</li>`
                        ).join('') : '<li>Consult local agricultural expert</li>'}
                    </ul>
                </div>
                
                ${result.advice.prevention ? `
                <div class="prevention-tips">
                    <h5><i class="fas fa-shield-alt"></i> Prevention:</h5>
                    <p>${result.advice.prevention}</p>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Chat functionality
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        });
        
        const data = await response.json();
        addMessage(data.response, 'ai');
    } catch (error) {
        addMessage('Sorry, I encountered an error. Please try again.', 'ai');
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${type === 'ai' ? 'KrishiMitra:' : 'You:'}</strong> ${text}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Set up navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            showSection(section);
        });
    });
    
    // Show dashboard by default
    showSection('dashboard');
});
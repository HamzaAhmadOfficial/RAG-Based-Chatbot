// API Base URL
const API_BASE_URL = window.location.origin;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');

// State
let isDocumentUploaded = false;
let sessionId = generateSessionId();

// Generate session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload button
    uploadBtn.addEventListener('click', () => fileInput.click());

    // File input
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Send button
    sendBtn.addEventListener('click', sendQuestion);

    // Enter key
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendBtn.disabled) {
            sendQuestion();
        }
    });

    // Clear button
    clearBtn.addEventListener('click', clearDatabase);
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
}

// File Selection Handler
function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
        showUploadStatus('Invalid file format. Please select a PDF document.', 'error');
        return;
    }

    uploadFile(file);
}

// Upload File
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showUploadStatus('Processing document...', 'loading');
    uploadBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();

        showUploadStatus(
            `${result.filename} processed successfully.`,
            'success'
        );

        isDocumentUploaded = true;
        enableChat();

        // Clear welcome message
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Add system message
        addSystemMessage(`System: Document "${result.filename}" is now active. You may proceed with your inquiry.`);

    } catch (error) {
        showUploadStatus(`Error: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
    }
}

// Show Upload Status
function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
}

// Enable Chat
function enableChat() {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    questionInput.focus();
}

// Send Question
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message
    addUserMessage(question);

    // Clear input
    questionInput.value = '';

    // Disable input while processing
    questionInput.disabled = true;
    sendBtn.disabled = true;

    // Show typing indicator
    const typingId = addTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to retrieve analysis');
        }

        const result = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add bot response
        addBotMessage(result.answer, result.sources);

    } catch (error) {
        removeTypingIndicator(typingId);
        addBotMessage(`Analysis Error: ${error.message}`);
    } finally {
        questionInput.disabled = false;
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// Add User Message
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add Bot Message
function addBotMessage(text, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <h4>Verified Sources</h4>
                ${sources.map((source, index) => `
                    <div class="source-item">
                        <strong>Source ${index + 1}:</strong> ${escapeHtml(source.title || 'Internal Document')} 
                        <br>
                        <em>${escapeHtml(source.text_preview || '')}</em>
                    </div>
                `).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            ${sourcesHtml}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add System Message
function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = `
        <div class="message-content" style="background: #f8fafc; border: 1px solid #e2e8f0; font-style: italic;">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add Typing Indicator
function addTypingIndicator() {
    const id = 'typing_' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.id = id;
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">Analyzing...</div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return id;
}

// Remove Typing Indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Clear Database
async function clearDatabase() {
    if (!confirm('This action will permanently delete all active sessions and uploaded data. Proceed?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/clear`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Database reset failed');
        }

        // Reset UI
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h3>Welcome to RAG Assistant</h3>
                <p>Please upload a document to begin the session. You can then ask specific questions regarding the document's content.</p>
                <div class="features">
                    <div class="feature">
                        <span>Semantic Analysis</span>
                    </div>
                    <div class="feature">
                        <span>Knowledge Retrieval</span>
                    </div>
                    <div class="feature">
                        <span>Contextual Citations</span>
                    </div>
                </div>
            </div>
        `;

        questionInput.disabled = true;
        sendBtn.disabled = true;
        isDocumentUploaded = false;
        showUploadStatus('System successfully reset.', 'success');

    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Scroll to Bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check server health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('Server status:', data.status);
    } catch (error) {
        console.error('Connection check failed:', error);
    }
}

checkHealth();

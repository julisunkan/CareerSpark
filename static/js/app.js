// AI Resume Optimizer - Main JavaScript Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 AI Resume Optimizer initialized');
    
    // Initialize components
    initializeFileUpload();
    initializeFormValidation();
    initializeTooltips();
    initializeProgressBars();
    initializeSearchAndFilter();
    initializeAnalyticsTracking();
    
    // Add smooth scrolling
    initializeSmoothScroll();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Performance monitoring
    monitorPerformance();
}

/**
 * Enhanced file upload with drag & drop
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('resume_file');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!fileInput || !uploadForm) return;
    
    // Create drag and drop area
    const dropArea = createDropArea(fileInput);
    
    // File validation
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            validateFile(file);
        }
    });
    
    // Drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    }
}

/**
 * Create drag and drop area
 */
function createDropArea(fileInput) {
    const formGroup = fileInput.closest('.mb-4');
    formGroup.classList.add('file-upload-area');
    return formGroup;
}

/**
 * Validate uploaded file
 */
function validateFile(file) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    // Type validation
    if (!allowedTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload PDF, DOCX, or TXT files only.', 'danger');
        return false;
    }
    
    // Size validation
    if (file.size > maxSize) {
        showAlert('File size exceeds 16MB limit. Please choose a smaller file.', 'danger');
        return false;
    }
    
    // Show file preview
    showFilePreview(file);
    return true;
}

/**
 * Show file preview
 */
function showFilePreview(file) {
    const preview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    if (preview && fileName && fileSize) {
        fileName.textContent = file.name;
        fileSize.textContent = `(${formatFileSize(file.size)})`;
        preview.style.display = 'block';
        preview.classList.add('fade-in');
    }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Enhanced form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

/**
 * Validate individual form
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Special validation for upload form
    if (form.id === 'uploadForm') {
        isValid = validateUploadForm(form) && isValid;
    }
    
    return isValid;
}

/**
 * Validate upload form specifically
 */
function validateUploadForm(form) {
    const fileInput = form.querySelector('#resume_file');
    const jobDescription = form.querySelector('#job_description');
    
    let isValid = true;
    
    // File validation
    if (!fileInput.files.length) {
        showFieldError(fileInput, 'Please select a resume file.');
        isValid = false;
    }
    
    // Job description validation
    if (jobDescription.value.trim().length < 50) {
        showFieldError(jobDescription, 'Job description must be at least 50 characters long.');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Validate individual field
 */
function validateField(field) {
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !field.value.trim()) {
        showFieldError(field, 'This field is required.');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            showFieldError(field, 'Please enter a valid email address.');
            return false;
        }
    }
    
    return true;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize progress bars with animation
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        // Animate to target width
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = targetWidth;
        }, 100);
    });
}

/**
 * Initialize search and filter functionality
 */
function initializeSearchAndFilter() {
    const searchInput = document.getElementById('searchResumes');
    const scoreFilter = document.getElementById('scoreFilter');
    const sortBy = document.getElementById('sortBy');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
    
    if (scoreFilter) {
        scoreFilter.addEventListener('change', performFilter);
    }
    
    if (sortBy) {
        sortBy.addEventListener('change', performSort);
    }
}

/**
 * Perform search functionality
 */
function performSearch() {
    const searchTerm = document.getElementById('searchResumes').value.toLowerCase();
    const items = document.querySelectorAll('.resume-item');
    
    items.forEach(item => {
        const filename = item.dataset.filename || '';
        const text = item.textContent.toLowerCase();
        
        if (filename.includes(searchTerm) || text.includes(searchTerm)) {
            item.style.display = 'block';
            item.classList.add('fade-in');
        } else {
            item.style.display = 'none';
        }
    });
    
    updateResultsCount();
}

/**
 * Perform filter functionality
 */
function performFilter() {
    const filterValue = document.getElementById('scoreFilter').value;
    const items = document.querySelectorAll('.resume-item');
    
    items.forEach(item => {
        const score = parseFloat(item.dataset.score) || 0;
        let shouldShow = true;
        
        switch (filterValue) {
            case 'excellent':
                shouldShow = score >= 80;
                break;
            case 'good':
                shouldShow = score >= 60 && score < 80;
                break;
            case 'fair':
                shouldShow = score >= 40 && score < 60;
                break;
            case 'poor':
                shouldShow = score < 40;
                break;
            default:
                shouldShow = true;
        }
        
        item.style.display = shouldShow ? 'block' : 'none';
    });
    
    updateResultsCount();
}

/**
 * Perform sort functionality
 */
function performSort() {
    const sortValue = document.getElementById('sortBy').value;
    const container = document.getElementById('resumeList');
    const items = Array.from(document.querySelectorAll('.resume-item'));
    
    items.sort((a, b) => {
        switch (sortValue) {
            case 'newest':
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            case 'oldest':
                return new Date(a.dataset.date) - new Date(b.dataset.date);
            case 'highest-score':
                return parseFloat(b.dataset.score) - parseFloat(a.dataset.score);
            case 'lowest-score':
                return parseFloat(a.dataset.score) - parseFloat(b.dataset.score);
            default:
                return 0;
        }
    });
    
    // Re-append items in new order
    items.forEach(item => container.appendChild(item));
}

/**
 * Update results count
 */
function updateResultsCount() {
    const visibleItems = document.querySelectorAll('.resume-item[style*="block"], .resume-item:not([style*="none"])').length;
    const totalItems = document.querySelectorAll('.resume-item').length;
    
    // Update count display if element exists
    const countElement = document.getElementById('resultsCount');
    if (countElement) {
        countElement.textContent = `Showing ${visibleItems} of ${totalItems} resumes`;
    }
}

/**
 * Initialize smooth scrolling
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + U for upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            const uploadLink = document.querySelector('a[href*="upload"]');
            if (uploadLink) uploadLink.click();
        }
        
        // Ctrl/Cmd + H for history
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            const historyLink = document.querySelector('a[href*="history"]');
            if (historyLink) historyLink.click();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                bootstrap.Modal.getInstance(openModal).hide();
            }
        }
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
}

/**
 * Create alert container if it doesn't exist
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Get icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialize analytics tracking
 */
function initializeAnalyticsTracking() {
    // Track button clicks
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent.trim();
            const category = this.closest('.card')?.querySelector('.card-title')?.textContent || 'General';
            
            // Mock analytics - replace with real analytics service
            console.log('Analytics:', { action, category, timestamp: new Date().toISOString() });
        });
    });
    
    // Track form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            console.log('Form submitted:', { formId: this.id, timestamp: new Date().toISOString() });
        });
    });
}

/**
 * Monitor performance
 */
function monitorPerformance() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        
        // Track if load time is concerning
        if (loadTime > 3000) {
            console.warn('Page load time exceeded 3 seconds');
        }
    });
    
    // Monitor navigation timing
    if ('navigation' in performance) {
        const navTiming = performance.getEntriesByType('navigation')[0];
        console.log('Navigation timing:', {
            domContentLoaded: navTiming.domContentLoadedEventEnd - navTiming.domContentLoadedEventStart,
            loadComplete: navTiming.loadEventEnd - navTiming.loadEventStart
        });
    }
}

/**
 * Character counter for textareas
 */
function updateCharacterCount(textarea, countElement, recommendation = null) {
    const count = textarea.value.length;
    countElement.textContent = `${count} characters`;
    
    if (recommendation) {
        if (count >= recommendation) {
            countElement.className = 'text-success small';
        } else if (count >= recommendation * 0.5) {
            countElement.className = 'text-warning small';
        } else {
            countElement.className = 'text-muted small';
        }
    }
}

/**
 * Initialize character counters
 */
document.addEventListener('DOMContentLoaded', function() {
    const jobDescription = document.getElementById('job_description');
    const charCount = document.getElementById('charCount');
    
    if (jobDescription && charCount) {
        jobDescription.addEventListener('input', function() {
            updateCharacterCount(this, charCount, 500);
        });
    }
});

/**
 * Print functionality for resume previews
 */
function printResume() {
    const printContent = document.getElementById('resumePreview');
    if (!printContent) return;
    
    const newWindow = window.open('', '_blank');
    newWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: white;
                    color: #333;
                }
                .resume-content { 
                    max-width: 8.5in; 
                    margin: 0 auto; 
                }
                @media print { 
                    body { margin: 0; padding: 0; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${printContent.innerHTML}
        </body>
        </html>
    `);
    
    newWindow.document.close();
    newWindow.focus();
    
    setTimeout(() => {
        newWindow.print();
        newWindow.close();
    }, 250);
}

/**
 * Resume preview zoom functionality
 */
let currentZoom = 1;

function zoomIn() {
    currentZoom = Math.min(2, currentZoom + 0.1);
    updateZoom();
}

function zoomOut() {
    currentZoom = Math.max(0.5, currentZoom - 0.1);
    updateZoom();
}

function resetZoom() {
    currentZoom = 1;
    updateZoom();
}

function updateZoom() {
    const preview = document.getElementById('resumePreview');
    if (preview) {
        preview.style.transform = `scale(${currentZoom})`;
        preview.style.transformOrigin = 'top left';
        
        // Update zoom indicator if it exists
        const zoomIndicator = document.getElementById('zoomIndicator');
        if (zoomIndicator) {
            zoomIndicator.textContent = `${Math.round(currentZoom * 100)}%`;
        }
    }
}

/**
 * Copy to clipboard functionality
 */
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert(successMessage, 'success', 2000);
        }).catch(() => {
            fallbackCopyToClipboard(text, successMessage);
        });
    } else {
        fallbackCopyToClipboard(text, successMessage);
    }
}

function fallbackCopyToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert(successMessage, 'success', 2000);
    } catch (err) {
        showAlert('Failed to copy to clipboard', 'danger');
    } finally {
        textArea.remove();
    }
}

/**
 * Export functions for global use
 */
window.resumeOptimizer = {
    showAlert,
    copyToClipboard,
    printResume,
    zoomIn,
    zoomOut,
    resetZoom,
    updateCharacterCount
};

// Console welcome message
console.log(`
🚀 AI Resume Optimizer
Built with ❤️ using free and open-source tools
Version: 1.0.0
`);

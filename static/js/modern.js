// DevPort Modern JavaScript - Enhanced Interactions

class DevPortUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupFormEnhancements();
        this.setupImageUpload();
        this.setupModals();
        this.setupAnimations();
        this.setupProfilePicture();
        this.setupSidebar();
        this.setupNotifications();
    }

    // Enhanced Form Interactions
    setupFormEnhancements() {
        // Add floating label effect
        const inputs = document.querySelectorAll('.form-input');
        inputs.forEach(input => {
            // Add focus/blur animations
            input.addEventListener('focus', (e) => {
                e.target.parentElement.classList.add('focused');
                this.animateElement(e.target, 'pulse');
            });

            input.addEventListener('blur', (e) => {
                if (!e.target.value) {
                    e.target.parentElement.classList.remove('focused');
                }
            });

            // Real-time validation feedback
            input.addEventListener('input', (e) => {
                this.validateField(e.target);
            });
        });

        // Enhanced button interactions
        const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.createRippleEffect(e);
            });
        });
    }

    // Advanced Image Upload with Preview
    setupImageUpload() {
        const uploadAreas = document.querySelectorAll('.image-upload-area');
        
        uploadAreas.forEach(area => {
            const input = area.querySelector('input[type="file"]');
            
            // Drag and drop functionality
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleImageUpload(files[0], area);
                }
            });

            // Click to upload
            area.addEventListener('click', () => {
                input.click();
            });

            // File input change
            if (input) {
                input.addEventListener('change', (e) => {
                    if (e.target.files.length > 0) {
                        this.handleImageUpload(e.target.files[0], area);
                    }
                });
            }
        });
    }

    // Handle image upload with preview
    handleImageUpload(file, uploadArea) {
        // Validate file
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('Image size should be less than 5MB', 'error');
            return;
        }

        // Show loading state
        uploadArea.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Uploading image...</p>
        `;

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.createElement('div');
            preview.className = 'image-preview';
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 12px; box-shadow: var(--shadow-soft);">
                <div class="image-actions" style="margin-top: 1rem;">
                    <button type="button" class="btn-secondary btn-sm" onclick="this.parentElement.parentElement.remove()">Remove</button>
                </div>
            `;
            
            uploadArea.innerHTML = '';
            uploadArea.appendChild(preview);
            
            // Animate preview appearance
            this.animateElement(preview, 'fadeIn');
        };
        
        reader.readAsDataURL(file);
    }

    // Enhanced Modal System
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const modals = document.querySelectorAll('.modal-overlay');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                const modal = document.getElementById(modalId);
                if (modal) {
                    this.openModal(modal);
                }
            });
        });

        modals.forEach(modal => {
            // Close on overlay click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modal.classList.contains('active')) {
                    this.closeModal(modal);
                }
            });

            // Close button
            const closeBtn = modal.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.closeModal(modal);
                });
            }
        });
    }

    openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus trap
        const focusableElements = modal.querySelectorAll('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }

    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Animation System
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        document.querySelectorAll('.dashboard-card, .form-container').forEach(el => {
            observer.observe(el);
        });

        // Stagger animations for lists
        const listItems = document.querySelectorAll('.sidebar-item');
        listItems.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('slide-up');
        });
    }

    // Profile Picture Enhancement
    setupProfilePicture() {
        const profileContainers = document.querySelectorAll('.profile-picture-container');
        
        profileContainers.forEach(container => {
            const img = container.querySelector('.profile-picture');
            const placeholder = container.querySelector('.profile-picture-placeholder');
            
            // Add hover effects
            if (img) {
                img.addEventListener('mouseenter', () => {
                    img.style.transform = 'scale(1.1)';
                });
                
                img.addEventListener('mouseleave', () => {
                    img.style.transform = 'scale(1)';
                });
            }

            // Add edit overlay on hover
            const editOverlay = document.createElement('div');
            editOverlay.className = 'profile-edit-overlay';
            editOverlay.innerHTML = `
                <div class="edit-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </div>
            `;
            
            editOverlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                cursor: pointer;
                color: white;
            `;
            
            container.appendChild(editOverlay);
            
            container.addEventListener('mouseenter', () => {
                editOverlay.style.opacity = '1';
            });
            
            container.addEventListener('mouseleave', () => {
                editOverlay.style.opacity = '0';
            });
        });
    }

    // Responsive Sidebar
    setupSidebar() {
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.portfolio-sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
                if (overlay) overlay.classList.toggle('active');
            });
        }

        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }

    // Notification System
    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 3000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    // Utility Functions
    animateElement(element, animationClass) {
        element.classList.add(animationClass);
        element.addEventListener('animationend', () => {
            element.classList.remove(animationClass);
        }, { once: true });
    }

    createRippleEffect(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const fieldName = field.name;
        
        let isValid = true;
        let message = '';
        
        // Basic validation rules
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required';
        } else if (fieldType === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        } else if (fieldName === 'password' && value && value.length < 8) {
            isValid = false;
            message = 'Password must be at least 8 characters long';
        }
        
        // Update field appearance
        const errorElement = field.parentElement.querySelector('.field-error');
        if (errorElement) errorElement.remove();
        
        if (!isValid) {
            field.classList.add('error');
            const error = document.createElement('div');
            error.className = 'field-error';
            error.textContent = message;
            error.style.cssText = 'color: #e53e3e; font-size: 0.875rem; margin-top: 0.25rem;';
            field.parentElement.appendChild(error);
        } else {
            field.classList.remove('error');
        }
        
        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        const notification = document.createElement('div');
        
        notification.className = `notification alert alert-${type}`;
        notification.style.cssText = `
            margin-bottom: 1rem;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
        
        // Click to dismiss
        notification.addEventListener('click', () => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        });
    }

    // Theme switching functionality
    switchTheme(themeName) {
        document.body.setAttribute('data-theme', themeName);
        localStorage.setItem('devport-theme', themeName);
        this.showNotification(`Switched to ${themeName} theme`, 'success');
    }

    // Initialize theme from localStorage
    initTheme() {
        const savedTheme = localStorage.getItem('devport-theme');
        if (savedTheme) {
            this.switchTheme(savedTheme);
        }
    }
}

// CSS for ripple animation
const rippleCSS = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;

// Add CSS to head
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.devPortUI = new DevPortUI();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DevPortUI;
}


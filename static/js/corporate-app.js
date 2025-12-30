/**
 * Corporate Application JavaScript
 * Sistema de Gestão Corporativo
 */

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Main application initialization
 */
function initializeApp() {
    initializeTooltips();
    initializePopovers();
    initializeForms();
    initializeDataTables();
    initializeCharts();
    initializeNotifications();
    initializeAnimations();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize form enhancements
 */
function initializeForms() {
    // Auto-focus first form input
    const firstInput = document.querySelector('form input:not([type="hidden"]):not([readonly])');
    if (firstInput) {
        firstInput.focus();
    }

    // Form validation styling
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Numeric inputs formatting
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Currency formatting
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Auto-save forms (optional)
    initializeAutoSave();
}

/**
 * Initialize data tables enhancements
 */
function initializeDataTables() {
    // Add search functionality to tables
    const searchableTables = document.querySelectorAll('.table-searchable');
    searchableTable.forEach(function(table) {
        addTableSearch(table);
    });

    // Add sorting functionality
    const sortableTables = document.querySelectorAll('.table-sortable');
    sortableTables.forEach(function(table) {
        addTableSorting(table);
    });

    // Responsive table handling
    handleResponsiveTables();
}

/**
 * Add search functionality to table
 */
function addTableSearch(table) {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Pesquisar na tabela...';
    
    table.parentNode.insertBefore(searchInput, table);
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

/**
 * Add sorting functionality to table
 */
function addTableSorting(table) {
    const headers = table.querySelectorAll('thead th');
    
    headers.forEach(function(header, index) {
        if (header.classList.contains('sortable')) {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort"></i>';
            
            header.addEventListener('click', function() {
                sortTable(table, index);
            });
        }
    });
}

/**
 * Sort table by column
 */
function sortTable(table, column) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isNumeric = !isNaN(parseFloat(rows[0].cells[column].textContent));
    
    rows.sort(function(a, b) {
        let aVal = a.cells[column].textContent.trim();
        let bVal = b.cells[column].textContent.trim();
        
        if (isNumeric) {
            return parseFloat(aVal) - parseFloat(bVal);
        } else {
            return aVal.localeCompare(bVal);
        }
    });
    
    const tbody = table.querySelector('tbody');
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

/**
 * Handle responsive tables
 */
function handleResponsiveTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(function(table) {
        if (!table.parentNode.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

/**
 * Initialize charts (if needed)
 */
function initializeCharts() {
    // Chart.js integration
    const chartElements = document.querySelectorAll('[data-chart]');
    
    chartElements.forEach(function(element) {
        const chartType = element.dataset.chart;
        const chartData = JSON.parse(element.dataset.chartData || '{}');
        
        // Initialize chart based on type
        switch(chartType) {
            case 'line':
                createLineChart(element, chartData);
                break;
            case 'bar':
                createBarChart(element, chartData);
                break;
            case 'pie':
                createPieChart(element, chartData);
                break;
        }
    });
}

/**
 * Initialize notifications system
 */
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });

    // Notification permission request
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

/**
 * Show desktop notification
 */
function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        return new Notification(title, {
            icon: '/static/img/logo.png',
            badge: '/static/img/badge.png',
            ...options
        });
    }
}

/**
 * Initialize page animations
 */
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(function() {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Scroll animations
    const observeElements = document.querySelectorAll('.animate-on-scroll');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        });

        observeElements.forEach(function(element) {
            observer.observe(element);
        });
    }
}

/**
 * Initialize auto-save functionality
 */
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('.auto-save');
    
    autoSaveForms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let saveTimeout;
        
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(function() {
                    autoSaveForm(form);
                }, 2000);
            });
        });
    });
}

/**
 * Auto-save form data to localStorage
 */
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    const formId = form.id || 'auto-save-form';
    localStorage.setItem(`auto-save-${formId}`, JSON.stringify(data));
    
    // Show save indicator
    showSaveIndicator();
}

/**
 * Load auto-saved form data
 */
function loadAutoSavedData(formId) {
    const saved = localStorage.getItem(`auto-save-${formId}`);
    
    if (saved) {
        const data = JSON.parse(saved);
        const form = document.getElementById(formId);
        
        if (form) {
            Object.keys(data).forEach(function(key) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    }
}

/**
 * Show save indicator
 */
function showSaveIndicator() {
    let indicator = document.querySelector('.save-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'save-indicator alert alert-success position-fixed';
        indicator.style.cssText = 'top: 100px; right: 20px; z-index: 1050; padding: 0.5rem 1rem;';
        indicator.innerHTML = '<i class="fas fa-check me-2"></i>Salvo automaticamente';
        document.body.appendChild(indicator);
    }
    
    indicator.style.opacity = '1';
    
    setTimeout(function() {
        indicator.style.opacity = '0';
    }, 2000);
}

/**
 * Utility functions
 */

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Format number
function formatNumber(value) {
    return new Intl.NumberFormat('pt-BR').format(value);
}

// Debounce function
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

// Throttle function  
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// AJAX helper
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Show loading state
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

// Hide loading state
function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Confirm action
function confirmAction(message = 'Tem certeza que deseja continuar?') {
    return confirm(message);
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1060';
    document.body.appendChild(container);
    return container;
}

/**
 * Export functions for global use
 */
window.CorporateApp = {
    formatCurrency,
    formatNumber,
    showNotification,
    showToast,
    confirmAction,
    makeRequest,
    showLoading,
    hideLoading,
    debounce,
    throttle
};
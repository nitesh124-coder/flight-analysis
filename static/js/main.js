// Main JavaScript for Airline Market Analyzer

// Global variables
let currentCharts = {};
let loadingStates = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

// Initialize application
function initializeApp() {
    console.log('🚀 Airline Market Analyzer initialized with enhanced UI');

    // Add loading states to forms
    setupFormLoadingStates();

    // Initialize tooltips
    initializeTooltips();

    // Setup responsive charts
    setupResponsiveCharts();

    // Add smooth scrolling
    setupSmoothScrolling();

    // Keep interactions minimal for a clean, modern feel
    simplifyInteractions();
}

// Setup event listeners
function setupEventListeners() {
    // Search form validation
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }
    
    // Route selection buttons
    const routeButtons = document.querySelectorAll('[onclick*="setRoute"]');
    routeButtons.forEach(button => {
        button.addEventListener('click', handleRouteSelection);
    });
    
    // Export buttons
    const exportButtons = document.querySelectorAll('[href*="api_data"]');
    exportButtons.forEach(button => {
        button.addEventListener('click', handleDataExport);
    });
    
    // Window resize for responsive charts
    window.addEventListener('resize', debounce(handleWindowResize, 250));
}

// Load initial data
function loadInitialData() {
    // Load dashboard stats if on dashboard page
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        loadDashboardStats();
    }
    
    // Load market trends if on trends page
    if (window.location.pathname === '/trends') {
        loadMarketTrends();
    }
}

// Setup form loading states
function setupFormLoadingStates() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
        });
    });
}

// Show loading state for buttons
function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.dataset.originalText = originalText;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;
    
    // Store loading state
    loadingStates[button.id] = {
        button: button,
        originalText: originalText
    };
}

// Hide loading state
function hideLoadingState(buttonId) {
    const state = loadingStates[buttonId];
    if (state) {
        state.button.innerHTML = state.originalText;
        state.button.disabled = false;
        delete loadingStates[buttonId];
    }
}

// Handle search form submission
function handleSearchSubmit(e) {
    const form = e.target;
    const origin = form.querySelector('#origin').value;
    const destination = form.querySelector('#destination').value;
    const dateFrom = form.querySelector('#date_from').value;
    const dateTo = form.querySelector('#date_to').value;
    
    // Validation
    if (origin === destination) {
        e.preventDefault();
        showAlert('Origin and destination cannot be the same!', 'warning');
        return false;
    }
    
    if (new Date(dateFrom) > new Date(dateTo)) {
        e.preventDefault();
        showAlert('From date cannot be after to date!', 'warning');
        return false;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    showLoadingState(submitBtn);
    
    return true;
}

// Handle route selection
function handleRouteSelection(e) {
    const button = e.target.closest('button');
    const onclick = button.getAttribute('onclick');
    
    // Extract origin and destination from onclick
    const matches = onclick.match(/setRoute\('([^']+)',\s*'([^']+)'\)/);
    if (matches) {
        const origin = matches[1];
        const destination = matches[2];
        
        // Set form values
        const originSelect = document.getElementById('origin');
        const destinationSelect = document.getElementById('destination');
        
        if (originSelect && destinationSelect) {
            originSelect.value = origin;
            destinationSelect.value = destination;
            
            // Add visual feedback
            button.classList.add('btn-success');
            setTimeout(() => {
                button.classList.remove('btn-success');
            }, 1000);
        }
    }
}

// Handle data export
function handleDataExport(e) {
    const button = e.target.closest('a');
    showLoadingState(button);
    
    // Simulate export process
    setTimeout(() => {
        hideLoadingState(button.id);
        showAlert('Data export completed!', 'success');
    }, 2000);
}

// Load dashboard statistics
function loadDashboardStats() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(error => {
            console.error('Error loading dashboard stats:', error);
        });
}

// Update dashboard statistics
function updateDashboardStats(data) {
    // Update popular routes if data is available
    if (data.popular_routes) {
        const routesList = document.querySelector('.list-group');
        if (routesList) {
            routesList.innerHTML = '';
            data.popular_routes.forEach(route => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between';
                listItem.innerHTML = `
                    <span>${route.route}</span>
                    <span class="badge bg-primary">${route.flights} flights</span>
                `;
                routesList.appendChild(listItem);
            });
        }
    }
    
    // Update price trends
    if (data.price_trends) {
        const trendElements = document.querySelectorAll('.price-trend');
        trendElements.forEach(element => {
            element.textContent = data.price_trends.change;
        });
    }
}

// Load market trends
function loadMarketTrends() {
    // This would typically fetch real data from the API
    console.log('Loading market trends...');
    
    // Animate trend cards
    const trendCards = document.querySelectorAll('.card');
    trendCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 100);
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup responsive charts
function setupResponsiveCharts() {
    // Make Plotly charts responsive
    window.addEventListener('resize', function() {
        Object.keys(currentCharts).forEach(chartId => {
            if (document.getElementById(chartId)) {
                Plotly.Plots.resize(chartId);
            }
        });
    });
}

// Setup smooth scrolling
function setupSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
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

// Handle window resize
function handleWindowResize() {
    // Resize charts
    Object.keys(currentCharts).forEach(chartId => {
        if (document.getElementById(chartId)) {
            Plotly.Plots.resize(chartId);
        }
    });
    
    // Adjust table responsiveness
    adjustTableResponsiveness();
}

// Adjust table responsiveness
function adjustTableResponsiveness() {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const wrapper = table.closest('.table-responsive');
        if (wrapper) {
            if (window.innerWidth < 768) {
                wrapper.style.fontSize = '0.875rem';
            } else {
                wrapper.style.fontSize = '';
            }
        }
    });
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertContainer, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

// Utility function: Debounce
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

// Utility function: Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-AU', {
        style: 'currency',
        currency: 'AUD'
    }).format(amount);
}

// Utility function: Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-AU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Chart creation helpers
function createChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Chart container ${containerId} not found`);
        return null;
    }
    
    try {
        Plotly.newPlot(containerId, data.data, data.layout, {
            responsive: true,
            displayModeBar: false,
            ...options
        });
        
        currentCharts[containerId] = true;
        return true;
    } catch (error) {
        console.error(`Error creating chart ${containerId}:`, error);
        return false;
    }
}

// Export functions for global access
window.AirlineAnalyzer = {
    showAlert,
    formatCurrency,
    formatDate,
    createChart,
    showLoadingState,
    hideLoadingState
};

// Modern smooth interactions
function simplifyInteractions() {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });

    // Add active states to navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, 5000);
    });
}

// Enhanced Loading Animation
function showEnhancedLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="loading-spinner"></span> Processing...';
    element.disabled = true;
    element.style.background = 'rgba(255, 255, 255, 0.1)';

    return () => {
        element.innerHTML = originalContent;
        element.disabled = false;
        element.style.background = '';
    };
}

// Smooth Page Transitions
function smoothPageTransition(url) {
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.95)';

    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

// Set route function (called from HTML)
function setRoute(origin, destination) {
    const originSelect = document.getElementById('origin');
    const destinationSelect = document.getElementById('destination');

    if (originSelect && destinationSelect) {
        originSelect.value = origin;
        destinationSelect.value = destination;

        // Add visual feedback with animation
        originSelect.style.transform = 'scale(1.05)';
        destinationSelect.style.transform = 'scale(1.05)';

        setTimeout(() => {
            originSelect.style.transform = 'scale(1)';
            destinationSelect.style.transform = 'scale(1)';
        }, 200);

        // Trigger change events
        originSelect.dispatchEvent(new Event('change'));
        destinationSelect.dispatchEvent(new Event('change'));

        // Enhanced visual feedback
        showAlert(`✈️ Route set to ${origin} → ${destination}`, 'success');
    }
}

// Clear form function with animation
function clearForm() {
    const form = document.getElementById('searchForm');
    if (form) {
        // Add clearing animation
        form.style.opacity = '0.5';
        form.style.transform = 'scale(0.98)';

        setTimeout(() => {
            form.reset();

            // Reset dates to default
            const today = new Date();
            const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

            const dateFrom = document.getElementById('date_from');
            const dateTo = document.getElementById('date_to');

            if (dateFrom) dateFrom.value = today.toISOString().split('T')[0];
            if (dateTo) dateTo.value = nextWeek.toISOString().split('T')[0];

            form.style.opacity = '1';
            form.style.transform = 'scale(1)';

            showAlert('🧹 Form cleared successfully', 'info');
        }, 200);
    }
}

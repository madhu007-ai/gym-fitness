/**
 * GymFitness Center - Main JavaScript
 * =====================================
 * Contains:
 * - Page load animations
 * - Auto-dismiss alerts
 * - Animated counters
 * - Smooth scroll effects
 * - Form enhancements
 */

// ============================================================
// Run when the page is fully loaded
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-dismiss flash messages after 4 seconds
    autoDissmissAlerts();
    
    // Animate stat numbers counting up
    animateCounters();
    
    // Add fade-in animation to main content
    animatePageLoad();
    
    // Highlight current nav link
    highlightCurrentNav();

    console.log('🏋️ GymFitness Center loaded!');
});

// ============================================================
// AUTO DISMISS ALERTS
// Automatically close success/info messages after 4 seconds
// ============================================================
function autoDissmissAlerts() {
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Use Bootstrap's dismiss method
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) bsAlert.close();
        }, 4000); // 4000ms = 4 seconds
    });
}

// ============================================================
// ANIMATED COUNTERS
// Makes numbers count up from 0 when visible
// ============================================================
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number, .stat-card-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                // Extract the number from text (handles "10K+" format too)
                const text = target.textContent;
                const num = parseInt(text.replace(/\D/g, ''));
                const suffix = text.replace(/[\d]/g, '');
                
                if (num > 0) {
                    countUp(target, 0, num, suffix, 1500);
                }
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// Helper: animate a number from start to end
function countUp(element, start, end, suffix, duration) {
    const range = end - start;
    const stepTime = Math.max(Math.floor(duration / range), 10);
    let current = start;
    
    const timer = setInterval(() => {
        current += Math.ceil(range / (duration / stepTime));
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = current + suffix;
        element.classList.add('counting');
    }, stepTime);
}

// ============================================================
// PAGE LOAD ANIMATIONS
// Adds fade-in to cards and sections as user scrolls
// ============================================================
function animatePageLoad() {
    // Cards fade in when they scroll into view
    const animatables = document.querySelectorAll(
        '.feature-card, .program-card, .stat-card, .dashboard-card, .facility-card, .trainer-card, .class-card'
    );
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Stagger the animations
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // Start them invisible
    animatables.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
}

// ============================================================
// HIGHLIGHT CURRENT NAV LINK
// Adds 'active' class to the current page's nav link
// ============================================================
function highlightCurrentNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.style.color = '#FF3D00';
            link.style.fontWeight = '700';
        }
    });
}

// ============================================================
// FORM UTILITIES (Global)
// ============================================================

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this? This cannot be undone.');
}

// Show a loading state on button click
function setLoading(button, text) {
    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
}

// ============================================================
// PROGRESS BAR ANIMATION
// Animate skill progress bars
// ============================================================
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.transition = 'width 1.2s ease';
                    bar.style.width = width;
                }, 100);
                observer.unobserve(bar);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// Run progress animation
animateProgressBars();

// ============================================================
// TOOLTIP INITIALIZATION
// Bootstrap tooltips for small action buttons
// ============================================================
const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
tooltipElements.forEach(el => new bootstrap.Tooltip(el));

// ============================================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ============================================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ============================================================
// NAVBAR SCROLL EFFECT
// Make navbar slightly more opaque when scrolled
// ============================================================
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.gym-navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.5)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    }
});

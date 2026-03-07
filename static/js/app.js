// DiabetiCare — Global JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // ─── Dark Mode Toggle ─────────────────────────
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('diabeticare-theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('diabeticare-theme', next);
            this.textContent = next === 'dark' ? '☀️' : '🌙';
        });
    }

    // Load saved font size
    const savedFont = localStorage.getItem('diabeticare-font') || 'medium';
    html.setAttribute('data-font', savedFont);

    // Load saved contrast
    const savedContrast = localStorage.getItem('diabeticare-contrast') || 'normal';
    html.setAttribute('data-contrast', savedContrast);

    // ─── Mobile Nav Toggle ────────────────────────
    const navToggle = document.getElementById('nav-toggle');
    const navbarNav = document.getElementById('navbar-nav');

    if (navToggle && navbarNav) {
        navToggle.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
            this.textContent = navbarNav.classList.contains('show') ? '✕' : '☰';
        });

        // Close nav when clicking a link
        navbarNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navbarNav.classList.remove('show');
                navToggle.textContent = '☰';
            });
        });
    }

    // ─── Auto-dismiss alerts ──────────────────────
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // ─── Animate elements on scroll ───────────────
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .quick-action, .education-card').forEach(el => {
        observer.observe(el);
    });

    // ─── Tour functionality ───────────────────────
    const tourSteps = document.querySelectorAll('.tour-step');
    const tourDots = document.querySelectorAll('.tour-dot');
    let currentStep = 0;

    window.nextTourStep = function() {
        if (currentStep < tourSteps.length - 1) {
            tourSteps[currentStep].classList.remove('active');
            tourDots[currentStep].classList.remove('active');
            currentStep++;
            tourSteps[currentStep].classList.add('active');
            tourDots[currentStep].classList.add('active');
        }
    };

    window.prevTourStep = function() {
        if (currentStep > 0) {
            tourSteps[currentStep].classList.remove('active');
            tourDots[currentStep].classList.remove('active');
            currentStep--;
            tourSteps[currentStep].classList.add('active');
            tourDots[currentStep].classList.add('active');
        }
    };

    // ─── Form validation visual feedback ──────────
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim()) {
                this.style.borderColor = 'var(--success)';
            }
        });
        input.addEventListener('focus', function() {
            this.style.borderColor = 'var(--primary)';
        });
    });
});

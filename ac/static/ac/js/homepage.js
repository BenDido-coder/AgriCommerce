document.addEventListener('DOMContentLoaded', function() {
    // === Smooth Scrolling for Anchor Links ===
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href'))?.scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // === Scroll Animations ===
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });

    // === Animated Counters ===
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    document.querySelectorAll('.count-up').forEach(counter => {
        const target = parseInt(counter.dataset.count);
        if (!isNaN(target)) {
            animateValue(counter, 0, target, 2000);
        }
    });

    // === Search Functionality ===
    const searchBar = document.querySelector('.search-bar');
    if (searchBar) {
        const searchButton = searchBar.querySelector('button');
        searchButton.addEventListener('click', function() {
            const searchTerm = searchBar.querySelector('input').value;
            alert('Searching for: ' + searchTerm);
        });
    }

    // === Newsletter Subscription ===
    const newsletterForm = document.querySelector('.footer-links form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            alert('Thank you for subscribing with: ' + email);
            this.reset();
        });
    }

    // === Contact Form (footer) ===
    const footerContactForm = document.querySelector('.contact-form form');
    if (footerContactForm) {
        footerContactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }

    // === Contact Form with Loading Button ===
    const loadingForm = document.getElementById('contactForm');
    if (loadingForm) {
        loadingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button[type="submit"]');
            const text = btn.querySelector('.submit-text');
            const spinner = btn.querySelector('.spinner');

            if (btn && text && spinner) {
                btn.disabled = true;
                text.style.opacity = '0';
                spinner.style.display = 'block';

                setTimeout(() => {
                    alert('Message sent successfully!');
                    btn.disabled = false;
                    text.style.opacity = '1';
                    spinner.style.display = 'none';
                    this.reset();
                }, 2000);
            } else {
                alert('Your message has been sent! We will respond shortly.');
                this.reset();
            }
        });
    }

    // === FAQ Toggle Interaction ===
    document.querySelectorAll('.faq-item h3').forEach(item => {
        item.addEventListener('click', () => {
            item.nextElementSibling.classList.toggle('active');
        });
    });
});

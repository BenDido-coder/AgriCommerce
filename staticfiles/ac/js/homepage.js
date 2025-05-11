// You can add JavaScript functionality here
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Search functionality
    const searchBar = document.querySelector('.search-bar');
    if(searchBar) {
        const searchButton = searchBar.querySelector('button');
        searchButton.addEventListener('click', function() {
            const searchTerm = searchBar.querySelector('input').value;
            alert('Searching for: ' + searchTerm);
            // In a real implementation, you would redirect to search results or make an API call
        });
    }

    // Newsletter subscription
    const newsletterForm = document.querySelector('.footer-links form');
    if(newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            alert('Thank you for subscribing with: ' + email);
            this.reset();
        });
    }

    // Contact form submission
    const contactForm = document.querySelector('.contact-form form');
    if(contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
});
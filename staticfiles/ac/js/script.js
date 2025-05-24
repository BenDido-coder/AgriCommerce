// Form Submission Handling
document.getElementById('contactForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Your message has been sent! We will respond shortly.');
    this.reset();
});

// FAQ Interaction
document.querySelectorAll('.faq-item h3').forEach(item => {
    item.addEventListener('click', () => {
        const answer = item.nextElementSibling;
        answer.classList.toggle('active');
    });
});

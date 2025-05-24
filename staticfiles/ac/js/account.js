// Section switching
document.querySelectorAll('.account-nav a').forEach(tab => {
    tab.addEventListener('click', (e) => {
        e.preventDefault();
        const target = tab.dataset.target;
        document.querySelectorAll('.active-section').forEach(s => s.classList.remove('active-section'));
        document.querySelector(target).classList.add('active-section');
    });
});

// Modal handling
document.querySelectorAll('[data-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
        const modalId = btn.dataset.modal;
        document.getElementById(modalId).style.display = 'block';
    });
});

// Close modals
document.querySelectorAll('.close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.closest('.modal').style.display = 'none';
    });
});
document.addEventListener('DOMContentLoaded', function () {
    // Get current theme from localStorage or default to 'default'
    const savedTheme = localStorage.getItem('theme') || 'default';
    const body = document.body;
    
    // Apply saved theme on load
    body.classList.remove('theme-light', 'theme-dark');
    if (savedTheme !== 'default') {
        body.classList.add(`theme-${savedTheme}`);
    }

    // Theme switcher functionality
    document.querySelectorAll('.theme-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.dataset.theme;
            
            // Remove all theme classes
            body.classList.remove('theme-light', 'theme-dark');
            
            // Apply selected theme
            if (theme !== 'default') {
                body.classList.add(`theme-${theme}`);
            }
            
            // Store preference
            localStorage.setItem('theme', theme);
            
            // Update UI indicators
            document.querySelectorAll('.theme-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Update theme indicator
            const indicator = document.querySelector('.theme-indicator');
            if (indicator) {
                indicator.className = `theme-indicator theme-${theme}`;
            }
        });
    });

    // Initialize active state
    document.querySelectorAll('.theme-item').forEach(item => {
        if (item.dataset.theme === savedTheme) {
            item.classList.add('active');
        }
    });
});
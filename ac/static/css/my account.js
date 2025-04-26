document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = {
        'profile-tab': 'profile-section',
        'products-tab': 'products-section',
        'orders-tab': 'orders-section'
    };

    for (const [tabId, sectionId] of Object.entries(tabs)) {
        document.getElementById(tabId).addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs and sections
            document.querySelectorAll('.account-nav a').forEach(a => a.classList.remove('active'));
            document.querySelectorAll('.account-main section').forEach(s => s.classList.remove('active-section'));
            
            // Add active class to clicked tab and corresponding section
            this.classList.add('active');
            document.getElementById(sectionId).classList.add('active-section');
        });
    }

    // Notifications dropdown functionality
    const notificationsBtn = document.getElementById('notifications-btn');
    const notificationsMenu = document.getElementById('notifications-menu');
    
    notificationsBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationsMenu.classList.toggle('show');
    });

    // Close notifications when clicking outside
    document.addEventListener('click', function() {
        notificationsMenu.classList.remove('show');
    });

    // Quick navigation buttons
    document.getElementById('quick-orders-btn').addEventListener('click', function() {
        switchToTab('orders-tab', 'orders-section');
    });

    document.getElementById('back-to-products-btn').addEventListener('click', function() {
        switchToTab('products-tab', 'products-section');
    });

    // Helper function for tab switching
    function switchToTab(tabId, sectionId) {
        document.querySelector('.account-nav a.active').classList.remove('active');
        document.querySelector('.account-main section.active-section').classList.remove('active-section');
        
        document.getElementById(tabId).classList.add('active');
        document.getElementById(sectionId).classList.add('active-section');
    }
});

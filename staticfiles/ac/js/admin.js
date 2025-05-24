document.addEventListener('DOMContentLoaded', function () {
    console.log('Admin JS initialized');

    // Initialize DataTables with proper config
    const usersTable = $('#usersTable').DataTable({
        responsive: true,
        ordering: false,
        paging: false,
        searching: true,
        info: false,
        // Critical for dynamic content
        drawCallback: function(settings) {
            console.log('Table redrawn - reattaching listeners');
            attachEventListeners();
        }
    });

    // Initial attachment
    attachEventListeners();

    // Event delegation for dynamic content
    document.body.addEventListener('click', function(event) {
        if (event.target.closest('.toggle-status')) {
            console.log('Delegated toggle click');
            handleToggleStatus(event.target.closest('.toggle-status'));
        }
        
        if (event.target.closest('.view-user')) {
            console.log('Delegated view click');
            handleViewUser(event.target.closest('.view-user'));
        }
    });
});

// Core Functions
function handleToggleStatus(button) {
    console.log('Toggle button:', button);
    if (!button) {
        console.error('No button found');
        return;
    }

    const userId = button.dataset.userId;
    console.log(`Toggling user ${userId}`);

    fetch(`/custom-admin/users/${userId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log(`Response status: ${response.status}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            updateUserInterface(button, data.is_active);
            showToast('Status updated successfully', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'danger');
    });
}

function updateUserInterface(button, isActive) {
    // Update button
    button.classList.toggle('btn-danger', !isActive);
    button.classList.toggle('btn-success', isActive);
    button.innerHTML = isActive ? '<i class="fas fa-ban"></i>' : '<i class="fas fa-check"></i>';

    // Update badge
    const badge = button.closest('tr').querySelector('.user-status');
    if (badge) {
        badge.textContent = isActive ? 'Active' : 'Suspended';
        badge.classList.toggle('bg-success', isActive);
        badge.classList.toggle('bg-danger', !isActive);
    } else {
        console.error('Badge not found');
    }
}

function attachEventListeners() {
    console.log('Attaching event listeners');
    
    // Direct listeners for initial elements
    document.querySelectorAll('.toggle-status').forEach(button => {
        button.addEventListener('click', () => {
            console.log('Direct toggle click');
            handleToggleStatus(button);
        });
    });

    document.querySelectorAll('.view-user').forEach(button => {
        button.addEventListener('click', () => {
            console.log('Direct view click');
            handleViewUser(button);
        });
    });
}

// ===== Helper Functions =====
function attachUserEventListeners() {
    // Manually attach to existing elements
    document.querySelectorAll('.toggle-status').forEach(button => {
        button.addEventListener('click', () => handleToggleStatus(button));
    });
    document.querySelectorAll('.view-user').forEach(button => {
        button.addEventListener('click', () => handleViewUser(button));
    });
}

function populateUserModal(data) {
    document.getElementById('user-fullname').textContent = data.full_name || 'N/A';
    document.getElementById('user-email').textContent = data.email || 'N/A';
    document.getElementById('user-phone').textContent = data.phone || 'N/A';
    document.getElementById('user-registered').textContent = 
        data.date_joined ? new Date(data.date_joined).toLocaleString() : 'N/A';
    document.getElementById('user-lastlogin').textContent = 
        data.last_login ? new Date(data.last_login).toLocaleString() : 'Never';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    const toastId = `toast-${Date.now()}`;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    new bootstrap.Toast(toast).show();
    
    // Auto-remove after 5 seconds
    setTimeout(() => toast.remove(), 5000);
}
// At the very top of admin.js
if (typeof bootstrap === 'undefined') {
    console.error('Bootstrap not loaded! Check script loading order');
    alert('Critical error: Required libraries not loaded. Please refresh the page.');
}
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin JS loaded - version 2.2');

    // Initialize DataTables with DOM preservation
    const usersTable = $('#usersTable').DataTable({
        responsive: true,
        ordering: false,
        paging: false,
        searching: true,
        info: false,
        dom: 't',
        autoWidth: false,
        destroy: false,
        retrieve: true,
        columnDefs: [
            { 
                targets: 3, 
                orderable: false,
                render: function(data, type, row) {
                    return $('<div>').html(data).html();
                }
            }
        ],
        createdRow: function(row, data, index) {
        // Re-initialize tooltips for each row
        $(row).find('[data-bs-toggle="tooltip"]').tooltip();
    }
    });

    // ===== User Status Toggle =====
    // jQuery form submission handler
    $('body').on('submit', '.toggle-status-form', function(e) {
        e.preventDefault();
        const form = $(this);
        
        $.ajax({
            type: "POST",
            url: form.attr('action'),
            data: form.serialize(),
            success: function(data) {
                if(data.success) {
                    const button = form.find('button');
                    const isActive = data.is_active;
                    
                    // Update button styling
                    button.toggleClass('btn-danger btn-success', !isActive);
                    button.html(isActive ? 
                        '<i class="fas fa-ban"></i>' : 
                        '<i class="fas fa-check"></i>');

                    // Update status badge
                    const badge = form.closest('tr').find('.user-status');
                    badge.toggleClass('bg-success bg-danger', !isActive)
                          .text(isActive ? 'Active' : 'Suspended');
                    
                    showToast(`User ${isActive ? 'activated' : 'suspended'} successfully`, 'success');
                }
            },
            error: function(xhr) {
                showToast(`Error: ${xhr.statusText}`, 'danger');
            }
        });
    });

    // ===== View User Modal =====
    $(document).on('click', '.view-user', function() {
        handleViewUser(this);
    });

    // ===== Product Preview =====
    // Keep existing product preview handler
    document.querySelectorAll('.product-preview').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = e.target.dataset.productId;
            
            try {
                const response = await fetch(`/custom-admin/moderate-product/${productId}/`);
                const product = await response.json();
                
                // Populate modal
                document.getElementById('productPreviewName').textContent = product.name;
                document.getElementById('productPreviewSeller').textContent = product.seller;
                document.getElementById('productPreviewPrice').textContent = `${product.price} ETB`;
                document.getElementById('productPreviewCategory').textContent = product.category;
                document.getElementById('productPreviewDescription').textContent = product.description;
                document.getElementById('productPreviewCreated').textContent = product.created_at;
                
                const imgElement = document.getElementById('productPreviewImage');
                if (product.image_url) {
                    imgElement.src = product.image_url;
                    imgElement.parentElement.style.display = 'block';
                } else {
                    imgElement.parentElement.style.display = 'none';
                }
                
                new bootstrap.Modal(document.getElementById('productPreviewModal')).show();
            } catch (error) {
                console.error('Error loading product details:', error);
            }
        });
    });
});

// ===== View User Functions =====
function handleViewUser(button) {
    const userId = button.dataset.userId;
    const modalEl = document.getElementById('userModal');
    
    // Ensure modal exists
    if (!modalEl) {
        console.error('User modal not found in DOM');
        return;
    }

    // Initialize modal once
    if (!window.userModal) {
        window.userModal = new bootstrap.Modal(modalEl);
    }

    fetch(`/custom-admin/users/${userId}/`)
    .then(response => {
        if (!response.ok) throw new Error('User not found');
        return response.json();
    })
    .then(data => {
        // Update modal content
        document.getElementById('user-fullname').textContent = data.full_name || 'N/A';
        document.getElementById('user-email').textContent = data.email || 'N/A';
        document.getElementById('user-phone').textContent = data.phone || 'N/A';
        document.getElementById('user-registered').textContent = 
            new Date(data.date_joined).toLocaleString();
        document.getElementById('user-lastlogin').textContent = 
            data.last_login ? new Date(data.last_login).toLocaleString() : 'Never';
        
        // Show modal
        window.userModal.show();
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to load user details', 'danger');
    });
}
// ===== Helper Functions =====
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

// Product Preview Handler
document.querySelectorAll('.product-preview').forEach(link => {
    link.addEventListener('click', async (e) => {
        e.preventDefault()
        const productId = e.target.dataset.productId
        
        try {
            const response = await fetch(`/custom-admin/moderate-product/${productId}/`)
            const product = await response.json()
            
            // Populate modal
            document.getElementById('productPreviewName').textContent = product.name
            document.getElementById('productPreviewSeller').textContent = product.seller
            document.getElementById('productPreviewPrice').textContent = `${product.price} ETB`
            document.getElementById('productPreviewCategory').textContent = product.category
            document.getElementById('productPreviewDescription').textContent = product.description
            document.getElementById('productPreviewCreated').textContent = product.created_at
            
            const imgElement = document.getElementById('productPreviewImage')
            if (product.image_url) {
                imgElement.src = product.image_url
                imgElement.parentElement.style.display = 'block'
            } else {
                imgElement.parentElement.style.display = 'none'
            }
            
            new bootstrap.Modal(document.getElementById('productPreviewModal')).show()
        } catch (error) {
            console.error('Error loading product details:', error)
        }
    })
})

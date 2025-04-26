document.addEventListener('DOMContentLoaded', function() {
    const editInfoBtn = document.getElementById('edit-info-btn');
    const farmInfoModal = document.getElementById('farm-info-modal');
    const farmInfoForm = document.getElementById('farm-info-form');
    const closeButtons = document.querySelectorAll('.close-btn');

    // Open modal and pre-fill form
    editInfoBtn.addEventListener('click', function() {
        // Get current values
        const currentFarmName = document.getElementById('farm-name').textContent;
        const currentOwnerName = document.getElementById('owner-name').textContent;
        const currentEmail = document.getElementById('email').textContent;
        const currentPhone = document.getElementById('phone').textContent;
        
        // Set form values
        document.getElementById('edit-farm-name').value = currentFarmName;
        document.getElementById('edit-owner-name').value = currentOwnerName;
        document.getElementById('edit-email').value = currentEmail;
        document.getElementById('edit-phone').value = currentPhone;
        
        farmInfoModal.style.display = 'block';
    });

    // Close modal
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.closest('.modal').id === 'farm-info-modal') {
                farmInfoModal.style.display = 'none';
            }
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === farmInfoModal) {
            farmInfoModal.style.display = 'none';
        }
    });

    // Form submission
    farmInfoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const farmName = document.getElementById('edit-farm-name').value;
        const ownerName = document.getElementById('edit-owner-name').value;
        const email = document.getElementById('edit-email').value;
        const phone = document.getElementById('edit-phone').value;
        
        // Validate inputs
        if (!farmName || !ownerName || !email || !phone) {
            alert('Please fill in all fields');
            return;
        }

        // Update profile information
        updateProfileInfo(farmName, ownerName, email, phone);
        
        // Close modal
        farmInfoModal.style.display = 'none';
        
        // Show success message
        alert('Farm information updated successfully!');
    });

    // Update profile information
    function updateProfileInfo(farmName, ownerName, email, phone) {
        document.getElementById('farm-name').textContent = farmName;
        document.getElementById('owner-name').textContent = ownerName;
        document.getElementById('email').textContent = email;
        document.getElementById('phone').textContent = phone;
        document.getElementById('username').textContent = farmName;
    }
});
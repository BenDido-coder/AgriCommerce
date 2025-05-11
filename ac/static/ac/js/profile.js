document.addEventListener('DOMContentLoaded', () => {
    // Profile Edit Modal
    const editModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    document.getElementById('edit-info-btn').addEventListener('click', () => editModal.show());

    // Form Submission Handling
    document.getElementById('profileForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/update_profile/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });
            
            const data = await response.json();
            if (data.success) {
                location.reload();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
// whatsapp.js - Updated Version
function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    
    // Handle numbers starting with 0
    if (cleaned.startsWith('0')) {
        return '+251' + cleaned.slice(1);
    }
    
    // Handle numbers starting with 251
    if (cleaned.startsWith('251')) {
        return '+' + cleaned;
    }
    
    // Return original if already in international format
    return phone.startsWith('+') ? phone : `+${phone}`;
}

function validateEthiopianNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return /^251(7|9)\d{8}$/.test(cleaned) ? cleaned : null;
}

function openWhatsApp(phone, message) {
    try {
        const cleanPhone = validateEthiopianNumber(phone);
        
        if (!cleanPhone) {
            console.error(`Invalid number: ${phone}`);
            return false;
        }

        // Use WhatsApp Web's native interface
        const whatsappWebUrl = `https://web.whatsapp.com/send?phone=${cleanPhone}&text=${encodeURIComponent(message)}`;
        
        const newWindow = window.open(
            whatsappWebUrl,
            '_blank',
            'width=1000,height=700,noopener,noreferrer'
        );
        
        if (!newWindow || newWindow.closed) {
            // Fallback to wa.me if popup blocked
            window.open(
                `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`,
                '_blank',
                'noopener,noreferrer'
            );
        }
        
        return true;
    } catch (error) {
        console.error('WhatsApp Error:', error);
        return false;
    }
}
// New broadcast function
function sendBulkWhatsApp(phoneNumbers, message, delay = 2000) {
    if (!phoneNumbers || phoneNumbers.length === 0) {
        alert('No recipients selected');
        return;
    }

    if (!message || message.trim() === '') {
        alert('Please enter a message');
        return;
    }

    let successCount = 0;
    let currentIndex = 0;

    function sendNext() {
        if (currentIndex >= phoneNumbers.length) {
            alert(`Broadcast complete. Successfully sent to ${successCount}/${phoneNumbers.length} recipients`);
            return;
        }

        const phone = phoneNumbers[currentIndex];
        const wasSuccessful = openWhatsApp(phone, message);
        
        if (wasSuccessful) {
            successCount++;
        }

        currentIndex++;
        setTimeout(sendNext, delay);
    }

    if (confirm(`Send broadcast to ${phoneNumbers.length} recipients?`)) {
        sendNext();
    }
}

function sendBroadcast() {
    const message = document.getElementById('broadcastMessage').value;
    const recipients = getSelectedPhoneNumbers();
    sendBulkWhatsApp(recipients, message);
}

// Utility function for checkbox selections
function getSelectedPhoneNumbers() {
    const checkboxes = document.querySelectorAll('.user-check:checked');
    return Array.from(checkboxes).map(checkbox => checkbox.dataset.phone);
}
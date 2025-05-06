
// In whatsapp.js
let lastClick = 0;

function openWhatsApp(phone, message) {
    if (Date.now() - lastClick < 2000) return;
    lastClick = Date.now();
    // rest of the function
}

function openWhatsApp(phone, message) {
    // Clean phone number
    const cleanPhone = phone.replace(/[\s()-]/g, '');
        // Default admin message if empty
    const defaultMessage = "Hello from AgriCommerce";
    const encodedMessage = encodeURIComponent(message || defaultMessage);
    window.open(`https://wa.me/${cleanPhone}?text=${encodedMessage}`, '_blank');
}

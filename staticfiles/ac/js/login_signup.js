// Tab switching functionality
const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const showRegister = document.getElementById('show-register');
const showLogin = document.getElementById('show-login');

function showLoginForm() {
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
}

function showRegisterForm() {
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
}

loginTab.addEventListener('click', showLoginForm);
registerTab.addEventListener('click', showRegisterForm);
showRegister.addEventListener('click', function(e) {
    e.preventDefault();
    showRegisterForm();
});
showLogin.addEventListener('click', function(e) {
    e.preventDefault();
    showLoginForm();
});

// Form validation
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        const formGroup = input.closest('.form-group');
        formGroup.classList.remove('error', 'success');
        
        if (input.required && !input.value.trim()) {
            formGroup.classList.add('error');
            isValid = false;
            return;
        }
        
        if (input.type === 'email' && !/^\S+@\S+\.\S+$/.test(input.value)) {
            formGroup.classList.add('error');
            isValid = false;
            return;
        }
        
        if (input.id === 'register-password' && input.value.length < 8) {
            formGroup.classList.add('error');
            isValid = false;
            return;
        }
        
        if (input.id === 'register-confirm' && 
            input.value !== document.getElementById('register-password').value) {
            formGroup.classList.add('error');
            isValid = false;
            return;
        }
        
        formGroup.classList.add('success');
    });
    
    return isValid;
}

// Form submission
document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    if (validateForm(this)) {
        // Here you would typically send the data to your server
        alert('Login successful! Redirecting to dashboard...');
        // window.location.href = 'dashboard.html';
    }
});

document.getElementById('register-form').addEventListener('submit', function(e) {
    e.preventDefault();
    if (validateForm(this)) {
        // Here you would typically send the data to your server
        alert('Registration successful! Please check your email for verification.');
        showLoginForm();
    }
});

// Input validation on blur
document.querySelectorAll('input, select').forEach(input => {
    input.addEventListener('blur', function() {
        const formGroup = this.closest('.form-group');
        if (this.required && !this.value.trim()) {
            formGroup.classList.add('error');
        } else {
            formGroup.classList.remove('error');
            formGroup.classList.add('success');
        }
    });
});

// Social login button functionality
document.querySelectorAll('.social-btn').forEach(button => {
    button.addEventListener('click', function() {
        const platform = this.classList.contains('facebook') ? 'Facebook' :
                        this.classList.contains('google') ? 'Google' : 'Twitter';
        alert(`Redirecting to ${platform} login...`);
        // In a real implementation, you would redirect to the OAuth endpoint
    });
});
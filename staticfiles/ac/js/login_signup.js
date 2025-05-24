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

        if (input.id === 'register-confirm') {
            const pw = document.getElementById('register-password');
            if (pw && input.value !== pw.value) {
                formGroup.classList.add('error');
                isValid = false;
                return;
            }
        }

        formGroup.classList.add('success');
    });

    return isValid;
}

// Signup form submission
document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    }

    // Input validation on blur
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('blur', function () {
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
        button.addEventListener('click', function () {
            const platform = this.classList.contains('facebook') ? 'Facebook' :
                            this.classList.contains('google') ? 'Google' : 'Twitter';
            alert(`Redirecting to ${platform} login...`);
        });
    });
});

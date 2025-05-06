document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Add loading spinner to submit button
    submitBtn.innerHTML = '<span>Sign Up</span><div class="spinner"></div>';
    
    // Add padding to inputs with icons
    const iconInputs = ['username', 'email', 'password1', 'password2'];
    iconInputs.forEach(id => {
      const input = document.getElementById(`id_${id}`);
      if (input) {
        input.style.paddingLeft = '45px';
      }
});
});

    // You can add JavaScript functionality here
document.addEventListener('DOMContentLoaded', function() {
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
          e.preventDefault();
          
          document.querySelector(this.getAttribute('href')).scrollIntoView({
              behavior: 'smooth'
          });
      });
  });
    
    // Password strength indicator
    const passwordInput = document.getElementById('id_password1');
    if (passwordInput) {
      const strengthMeter = document.createElement('div');
      strengthMeter.className = 'password-strength';
      strengthMeter.innerHTML = `
        <div class="strength-bar"></div>
        <div class="strength-text"></div>
      `;
      passwordInput.parentNode.insertBefore(strengthMeter, passwordInput.nextSibling);
      
      passwordInput.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        const bar = strengthMeter.querySelector('.strength-bar');
        const text = strengthMeter.querySelector('.strength-text');
        
        bar.style.width = `${strength}%`;
        
        if (strength < 30) {
          bar.style.backgroundColor = '#f44336';
          text.textContent = 'Weak';
        } else if (strength < 70) {
          bar.style.backgroundColor = '#FFC107';
          text.textContent = 'Medium';
        } else {
          bar.style.backgroundColor = '#4CAF50';
          text.textContent = 'Strong';
        }
      });
    }
    
    // Form submission
    form.addEventListener('submit', function(e) {
      // Client-side validation
      let isValid = true;
      
      // Check required fields
      const requiredFields = form.querySelectorAll('input[required], select[required]');
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.style.borderColor = '#f44336';
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        alert('Please fill in all required fields');
        return;
      }
      
      // Check password match
      const password1 = document.getElementById('id_password1');
      const password2 = document.getElementById('id_password2');
      if (password1 && password2 && password1.value !== password2.value) {
        e.preventDefault();
        password1.style.borderColor = '#f44336';
        password2.style.borderColor = '#f44336';
        alert('Passwords do not match');
        return;
      }
      
      // Show loading state
      submitBtn.disabled = true;
      submitBtn.querySelector('span').textContent = 'Creating Account...';
      submitBtn.querySelector('.spinner').style.display = 'block';
    });
    
    // Calculate password strength
    function calculatePasswordStrength(password) {
      let strength = 0;
      
      // Length
      if (password.length >= 8) strength += 30;
      if (password.length >= 12) strength += 20;
      
      // Complexity
      if (/[A-Z]/.test(password)) strength += 15;
      if (/[0-9]/.test(password)) strength += 15;
      if (/[^A-Za-z0-9]/.test(password)) strength += 20;
      
      return Math.min(strength, 100);
    }
    
    // Add focus/blur effects
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
      input.addEventListener('focus', function() {
        this.style.borderColor = '#4CAF50';
        this.style.boxShadow = '0 0 0 3px rgba(76, 175, 80, 0.2)';
      });
      
      input.addEventListener('blur', function() {
        this.style.borderColor = '#e0e0e0';
        this.style.boxShadow = 'none';
      });
    });
  });
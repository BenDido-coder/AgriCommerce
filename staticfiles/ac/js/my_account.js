document.addEventListener('DOMContentLoaded', () => {
    const sectionTabs = {
      'profile-tab': 'profile-section',
      'products-tab': 'products-section',
      'orders-tab': 'orders-section'
    };
  
    Object.keys(sectionTabs).forEach(tabId => {
      const tab = document.getElementById(tabId);
      if (tab) {
        tab.addEventListener('click', e => {
          e.preventDefault();
          document.querySelectorAll('.account-content > div').forEach(div => div.classList.remove('active-section'));
          document.querySelectorAll('.account-nav a').forEach(link => link.classList.remove('active'));
  
          document.getElementById(sectionTabs[tabId]).classList.add('active-section');
          tab.classList.add('active');
        });
      }
    });
  
    const editBtn = document.getElementById('edit-profile-btn');
    const editModalEl = document.getElementById('editProfileModal');
    if (editBtn && editModalEl) {
      editBtn.addEventListener('click', () => {
        const modal = new bootstrap.Modal(editModalEl);
        modal.show();
      });
    }
  
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
      profileForm.addEventListener('submit', async e => {
        e.preventDefault();
        const formData = new FormData(profileForm);
  
        try {
          const response = await fetch(profileForm.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': getCSRFToken()
            }
          });
  
          const result = await response.json();
          if (result.success) {
            document.getElementById('username').textContent = `${result.new_data.first_name} ${result.new_data.last_name}`;
            document.getElementById('email').textContent = result.new_data.email;
            document.getElementById('phone').textContent = result.new_data.phone;
            document.getElementById('i-am').textContent = result.new_data.role;
            document.getElementById('farm-name').textContent = result.new_data.farm_name || '';
            document.getElementById('location').textContent = result.new_data.location || '';
  
            bootstrap.Modal.getInstance(editModalEl).hide();
            alert('Profile updated successfully!');
          } else {
            alert('Error: ' + JSON.stringify(result.errors));
          }
        } catch (err) {
          console.error(err);
          alert('Something went wrong.');
        }
      });
    }
  
    function getCSRFToken() {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
      }
      return '';
    }
  });
  
    // Footer interactivity
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scrollToTop';
    scrollBtn.title = 'Back to Top';
    scrollBtn.innerHTML = '⬆️';
    document.body.appendChild(scrollBtn);
  
    scrollBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  
    window.addEventListener('scroll', () => {
      if (window.scrollY > 150) {
        scrollBtn.style.display = 'block';
      } else {
        scrollBtn.style.display = 'none';
      }
    });
  
    // Dynamic year in footer (if using a span with id="year")
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
      yearSpan.textContent = new Date().getFullYear();
    }
  
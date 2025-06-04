// Modified applyTheme function
function applyTheme(theme) {
  const root = document.documentElement;
  
  if(theme === 'system') {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.setAttribute('data-theme', systemDark ? 'dark' : 'light');
    localStorage.setItem('theme', 'system');
  } else {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }
  updateActiveButtons(theme);
}

// Simplified initialization
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'system';
  applyTheme(savedTheme);
}

// Dedicated button state handler
function updateActiveButtons(theme) {
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === theme);
  });
}

// Event listeners
document.addEventListener('DOMContentLoaded', initTheme);
document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
});
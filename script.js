window.addEventListener('DOMContentLoaded', () => {
    fetch('topbar.html')
      .then(response => response.text())
      .then(data => {
        const container = document.getElementById('topbar-container');
        container.innerHTML = data;
  
        // Set the active link
        const path = window.location.pathname.split('/').pop(); // e.g. "projects.html"
        const links = container.querySelectorAll('a[data-page]');
        links.forEach(link => {
          if (link.getAttribute('data-page') === path || (path === '' && link.getAttribute('data-page') === 'index.html')) {
            link.classList.add('active');
            link.setAttribute('href', '#');
          }
        });
      });
  });
  
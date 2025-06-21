window.addEventListener('DOMContentLoaded', () => {
    fetch('src/nav.html')
        .then(res => res.text())
        .then(html => {
            document.getElementById('nav-placeholder').innerHTML = html;
        })
        .catch(err => console.error('Failed to load nav:', err));
});
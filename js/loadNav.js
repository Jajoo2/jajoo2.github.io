window.addEventListener('DOMContentLoaded', () => {
    fetch('/src/nav.html')
        .then(res => res.text())
        .then(html => {
            const navContainer = document.getElementById('nav-placeholder');
            navContainer.innerHTML = html;

            var path = window.location.pathname;
            var page = path.split("/").pop();

            // loop through the list items
            const listItems = navContainer.querySelectorAll('li');
            listItems.forEach((li, index) => {
                // do something with each li element here
                // in this case, highlight it

                const anchor = li.querySelector('a');
                if (anchor) {
                    const href = anchor.getAttribute('href').replace("/", "");
                    const text = anchor.textContent.trim();
                    if (href.split(".")[0] == page.split(".")[0]) {
                        anchor.classList.add('navhover');
                        anchor.style.backgroundColor = "#9744aa";
                    }
                }

            });
        })
        .catch(err => console.error('Failed to load nav:', err));
});

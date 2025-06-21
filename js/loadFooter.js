window.addEventListener('DOMContentLoaded', () => {
    fetch('src/footer.html')
        .then(res => res.text())
        .then(html => {
            document.getElementById('footer-placeholder').innerHTML = html;
        })
        .catch(err => console.error('Failed to load nav:', err));
});

/*
<div style="display: flex; align-items: center; gap: 30px;"> <!--Text bit-->
                <p>&copy; 2025 Meisite. All rights reserved.<br>Made with love and HTML</p>
                <a href="/contact.html">Contact</a>
            </div>

            <div> <!--Image bit-->
                <img class="badge" src="img/mei.png" width="50px">
                <img class="badge" src="img/meicon.svg" width="50px" style="border: none;">
            </div>*/
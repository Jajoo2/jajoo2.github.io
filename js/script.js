// Runs for EVERY page

function showToast(str,timeout=2000)
{
    var toast = document.createElement('div');
    var toastcontainer = document.getElementById("toast-container")
    if(!toastcontainer)
    {
        console.error("Fired toast but no toast-container");
        return 0
    }
    toast.innerHTML = str;
    toast.className = "toast";
    toastcontainer.appendChild(toast)
    toast.style.animation = `pop ${(timeout+100) / 1000}s ease-out`;
    setTimeout(function() {toastcontainer.removeChild(toast)},timeout);
}

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById("sidebar")

    document.head.innerHTML += '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">\n<link href="https://fonts.googleapis.com/icon?family=Material+Symbols" rel="stylesheet">\n<link href="https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined" rel="stylesheet">\n<link href="https://fonts.googleapis.com/css2?family=Material+Icons+Outlined" rel="stylesheet"></link>'

    fetch('/src/links.html')
        .then(r => r.text())
        .then(html => {
            sidebar.innerHTML += html
        })


    window.addEventListener('mousemove', e => {
        const x = e.clientX
        if (x < 10) 
        {
            sidebar.style.transform = "translateX(0)"
        }
        if (x > window.innerWidth * 0.15)
        {
            sidebar.style.transform = "translateX(-17vw)"
        }
    })
})


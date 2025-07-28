function toastnotify(ntext) {
    const div = document.createElement("div");
    div.className = "toast";
    div.innerHTML = `<p>${ntext}</p>`;

    const container = document.getElementById("toast-container");
    container.appendChild(div);

    // Ensure transition applies
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            div.style.transform = "translateY(0)";
            div.style.opacity = "1";
        });
    });

    setTimeout(() => {
        div.style.opacity = "0";
        div.style.transform = "scale(0.9)";
        div.addEventListener("transitionend", () => {
            div.remove();
        }, { once: true });
    }, 1500);
}

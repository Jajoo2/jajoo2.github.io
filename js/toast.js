function toastnotify(ntext) {
    const div = document.createElement("div");
    div.className = "toast";
    function replaceEmojiCodes(text) {
        return text.replace(/:([a-zA-Z0-9_-]+):/g, (match, filename) => {
            return `<span style="display:inline-flex; align-items:center; vertical-align:middle;">
                    <img src="img/emoji/${filename}.gif" alt="${filename}" style="height:1.5em; width:auto;"/>
                  </span>`;
        });
    }
    

    div.innerHTML = `<p>${replaceEmojiCodes(ntext)}</p>`;

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

function toastnotify(ntext) {
    const div = document.createElement("div");
    div.id = "toast";
    div.innerHTML = `<p>${ntext}</p>`;

    document.getElementById("toast-container").appendChild(div);

    // First rAF to ensure element is in DOM with initial styles
    requestAnimationFrame(() => {
        // Second rAF to apply final styles and trigger transition
        requestAnimationFrame(() => {
            div.style.marginTop = "10px";
            div.style.opacity = "1";
        });
    });


    setTimeout(() => {
        div.style.opacity = "0";

        div.addEventListener("transitionend", () => {
            div.remove();
        }, { once: true });
    }, 1500);

}
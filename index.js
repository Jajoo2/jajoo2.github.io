const link = document.createElement("link");
link.rel = "icon"
link.type = "image/x-icon"
link.href = "img/mei.png"
document.head.appendChild(link);

function replaceEmojiCodes(text) {
    return text.replace(/:([a-zA-Z0-9_-]+):/g, (match, filename) => {
        return `<span style="display:inline-flex; align-items:center; vertical-align:middle;">
            <img src="img/emoji/${filename}.gif" alt="${filename}" style="height:1.5em; width:auto;"/>
          </span>`;
    });
}

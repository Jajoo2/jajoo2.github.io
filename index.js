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


function compressImage(file, maxSizeMB = 10) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const reader = new FileReader();

        reader.onload = (e) => {
            img.src = e.target?.result;
        };
        reader.onerror = () => reject("file read error");
        reader.readAsDataURL(file);

        img.onload = () => {
            const canvas = document.createElement("canvas");
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);

            let quality = 0.9;

            const step = () => {
                canvas.toBlob(
                    (blob) => {
                        if (!blob) return reject("compression failed");

                        if (blob.size / (1024 * 1024) <= maxSizeMB || quality <= 0.1) {
                            const fr = new FileReader();
                            fr.onload = () => resolve(fr.result);
                            fr.readAsDataURL(blob);
                        } else {
                            quality -= 0.1;
                            step();
                        }
                    },
                    "image/jpeg",
                    quality
                );
            };

            step();
        };

        img.onerror = () => reject("image load error");
    });
}
if (location.search.includes('utm_source'))
  alert("no. bad. no tracking tags on my turf.");

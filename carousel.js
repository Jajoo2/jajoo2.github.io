const track = document.getElementById('carouselTrack');
const images = track.children;
let currentIndex = 0;

function updateCarousel() {
    const offset = -currentIndex * 500; // 300 = image width
    track.style.transform = `translateX(${offset}px)`;
}

function nextImage() {
    if (currentIndex < images.length - 1) {
        currentIndex++;
        updateCarousel();
    }
}

function prevImage() {
    if (currentIndex > 0) {
        currentIndex--;
        updateCarousel();
    }
}
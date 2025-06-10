function setupCarousel() {
  const slider = document.querySelector(".content_inner_slider");
  const images = slider.querySelectorAll(".img");
  const dotsContainer = document.querySelector(".dots");
  const prev = document.querySelector(".prev_button");
  const next = document.querySelector(".next_button");
  const autoSlideCheckbox = document.querySelector("#slide");

  let index = 0;
  let intervalId = null;

  // Clear any old dots and create fresh ones
  dotsContainer.innerHTML = "";
  images.forEach((_, i) => {
    const dot = document.createElement("li");
    dot.className = "dot";
    dot.setAttribute("data-index", i);
    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll(".dot");

  const updateCarousel = () => {
    const width = slider.clientWidth;
    slider.style.transform = `translateX(-${width * index}px)`;
    dots.forEach(dot => {
      dot.style.background = "transparent";
      dot.style.transform = "scale(1)"; // reset scale for inactive dots
    });

    if (dots[index]) {
      dots[index].style.background = "#FFF";
      dots[index].style.transform = "scale(1.5)";
    }

  };

  const nextImage = () => {
    index = (index + 1) % images.length;
    updateCarousel();
  };

  const prevImage = () => {
    index = (index - 1 + images.length) % images.length;
    updateCarousel();
  };

  next.addEventListener("click", nextImage);
  prev.addEventListener("click", prevImage);

  dots.forEach(dot => {
    dot.addEventListener("click", (e) => {
      index = parseInt(e.target.getAttribute("data-index"));
      updateCarousel();
    });
  });

  autoSlideCheckbox.addEventListener("change", (e) => {
    if (e.target.checked) {
      intervalId = setInterval(nextImage, 2000);
    } else {
      clearInterval(intervalId);
    }
  });

  window.addEventListener("resize", updateCarousel);
  updateCarousel();
}

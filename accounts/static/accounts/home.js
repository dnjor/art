// Animation library AOS
document.addEventListener("DOMContentLoaded", function () {
    AOS.init({
    duration: 800,
    once: true
    });
});


//count numbers in the index
console.log('home.js loaded');
const countUpElements = document.querySelectorAll('.animation-count-up');

countUpElements.forEach(element => {
    const target = Number(element.getAttribute("data-target"));
    element.innerText = "0";

    const updateCount = () => {
        const current = Number(element.innerText);
        const increment = target / 500;

        if (current < target) {
            element.innerText = `${Math.min(Math.ceil(current + increment), target)}`;
            setTimeout(updateCount, 10);
        }
        else {
            element.innerText = target;
        }
    };

    updateCount();
});


//loop for pic in the index sesstion 3
document.addEventListener('DOMContentLoaded', function () {
    const images = document.querySelectorAll(".image-loop");
    let current = 0;

    setInterval(() => {
        images[current].classList.remove("active");
        current = (current + 1) % images.length;
        images[current].classList.add("active");
    }, 5000); // Change image every 5 seconds
})
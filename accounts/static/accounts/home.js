document.addEventListener("DOMContentLoaded", () => {
    if (window.AOS) {
        AOS.init({
            duration: 800,
            once: true,
        });
    }

    startCountUpAnimation();
    startImageLoop();
    startReviewLoop();
    loadGalleryPaintings();
    loadWorkShop();
});

function startCountUpAnimation() {
    const countUpElements = document.querySelectorAll(".animation-count-up");

    countUpElements.forEach((element) => {
        const target = Number(element.getAttribute("data-target"));
        element.innerText = "0";

        const updateCount = () => {
            const current = Number(element.innerText);
            const increment = target / 500;

            if (current < target) {
                element.innerText = `${Math.min(Math.ceil(current + increment), target)}`;
                setTimeout(updateCount, 10);
            } else {
                element.innerText = `${target}`;
            }
        };

        updateCount();
    });
}

function startImageLoop() {
    const images = document.querySelectorAll(".image-loop");

    if (!images.length) {
        return;
    }

    let current = 0;

    setInterval(() => {
        images[current].classList.remove("active");
        current = (current + 1) % images.length;
        images[current].classList.add("active");
    }, 5000);
}


function startReviewLoop() {
    const review = document.querySelectorAll(".review-loop");
    let current = 0;


    if (review.length > 1) {
        setInterval(() => {
            review[current].classList.remove("active");
            current = (current + 1) % review.length;
            review[current].classList.add("active");
        }, 5000);
    }
}

function waitForNextFrame() {
    return new Promise(requestAnimationFrame);
}

async function loadGalleryPaintings() {
    const container = document.querySelector(".gallery-container");
    const template = document.getElementById("painting-card-template");
    const loader = document.getElementById("loader");

    if (!container || !template || !loader) {
        return;
    }

    loader.classList.remove("hidden")
    await waitForNextFrame();

    try {
        const response = await fetch(container.dataset.galleryApiUrl, {
            credentials: "same-origin",
        });

        if (!response.ok) {
            throw new Error("لم يتم تحميل المعرض...");
        }

        const paintings = await response.json();
        container.innerHTML = "";

        paintings.forEach((painting) => {
            const clone = template.content.cloneNode(true);

            const cardLinks = clone.querySelectorAll(".link-painting");
            const imageElement = clone.querySelector(".image-painting");
            const titleElement = clone.querySelector(".title-painting");
            const descriptionElement = clone.querySelector(".description-painting");
            const updateElement = clone.querySelector(".update-painting");
            const deleteElement = clone.querySelector(".delete-painting");

            const detailUrl = `${container.dataset.detailBaseUrl}${painting.id}/`;
            const updateUrl = `${container.dataset.updateBaseUrl}${painting.id}/`;
            const deleteUrl = `${container.dataset.deleteBaseUrl}${painting.id}/`;

            cardLinks.forEach((linkElement) => {
                linkElement.href = detailUrl;
            });

            imageElement.src = painting.picture;
            imageElement.alt = painting.title;
            titleElement.textContent = painting.title;
            descriptionElement.textContent = painting.description || "";

            if (updateElement) {
                updateElement.href = updateUrl;
            }

            if (deleteElement) {
                deleteElement.href = deleteUrl;
            }

            container.appendChild(clone);
        });
    } catch (error) {
        console.error("Error loading gallery:", error);
        container.innerHTML = "<p>Could not load the gallery right now.</p>";
    } finally {
        loader.classList.add("hidden");
    }
}

// workshop page
async function loadWorkShop() {
    const container = document.querySelector(".workshop-container");
    const template = document.getElementById("workshop-card-template");
    const loader = document.getElementById("loader");
    const review = document.querySelector(".rate-showcase");

    if (!container || !template || !loader) {
        return;
    }

    loader.classList.remove("hidden");
    review.classList.add("hidden");

    try {
        const response = await fetch(container.dataset.workshopApiUrl, {
            credentials: "same-origin",
        });

        if (!response.ok) {
            throw new Error("لم يتم تحميل المعرض...");
        }

        const workshops = await response.json();
        container.innerHTML = "";

        workshops.forEach((workshop) => {
            const clone = template.content.cloneNode(true);

            const cardLinks = clone.querySelectorAll(".link-workshop");
            const imageElement = clone.querySelector(".image-workshop");
            const titleElement = clone.querySelector(".title-workshop");
            const statusElement = clone.querySelector(".status-workshop");
            const updateElement = clone.querySelector(".link-workshop-update");
            const deadLineElement = clone.querySelector(".dead-line");


            const detailUrl = `${container.dataset.detailBaseUrl}${workshop.id}/`;
            const updateUrl = `${container.dataset.updateBaseUrl}${workshop.id}/`;


            cardLinks.forEach((linkElement) => {
                linkElement.href = detailUrl;
            });

            imageElement.src = workshop.image;
            imageElement.alt = workshop.title;
            titleElement.textContent = workshop.title;
            statusElement.textContent = workshop.status;

            if (workshop.status === "open") {
                deadLineElement.textContent = workshop.deadline;
            }

            if (updateElement) {
                updateElement.href = updateUrl;
            }

            container.appendChild(clone);
        });
    } catch (error) {
        console.error("Error loading workshop:", error);
        container.innerHTML = "<div class='content-card'><p>لا توجد ورش عمل حالياً.</p> </div>";
    } finally {
        loader.classList.add("hidden");
        review.classList.remove("hidden");
    }
}

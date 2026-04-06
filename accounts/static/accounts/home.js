const countUpElements = document.querySelectorAll('.animation-count-up');

countUpElements.forEach(element => {
    const target = Number(element.getAttribute("data-target"));
    element.innerText = "0";

    const updateCount = () => {
        const current = Number(element.innerText);
        const increment = target / 500;

        if (current < target) {
            element.innerText = `${Math.min(Math.ceil(current + increment), target)}`;
            console.log(element.innerText);
            setTimeout(updateCount, 10);
        }
        else{
            element.innerText = target;
        }
    };

    updateCount();
    });
document.addEventListener("DOMContentLoaded", () => {

    // ---------------------------------------------------
    // Close flash messages
    // ---------------------------------------------------

    const closeButtons = document.querySelectorAll(
        ".alert-close"
    );

    closeButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const alert = button.closest(".alert");

            if (alert) {
                alert.remove();
            }

        });

    });


    // ---------------------------------------------------
    // Confirm resource deletion
    // ---------------------------------------------------

    const deleteForms = document.querySelectorAll(
        ".delete-form"
    );

    deleteForms.forEach((form) => {

        form.addEventListener("submit", (event) => {

            const resourceName =
                form.dataset.resourceName ||
                "this resource";

            const confirmed = window.confirm(
                `Delete "${resourceName}"?\n\n` +
                "This action will remove the resource " +
                "from the directory."
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    // ---------------------------------------------------
    // Description character counter
    // ---------------------------------------------------

    const description =
        document.getElementById("description");

    const counter =
        document.querySelector(
            '[data-counter-for="description"]'
        );

    if (description && counter) {

        const updateCounter = () => {

            counter.textContent =
                `${description.value.length}/1000`;

        };

        description.addEventListener(
            "input",
            updateCounter
        );

        updateCounter();

    }

});
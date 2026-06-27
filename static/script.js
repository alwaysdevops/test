const form = document.querySelector(".registration-form");

if (form) {
    form.addEventListener("submit", (event) => {
        const requiredFields = Array.from(form.querySelectorAll("[required]"));
        const missingField = requiredFields.find((field) => !field.value.trim());

        if (missingField) {
            event.preventDefault();
            missingField.focus();
        }
    });
}

// ------------------------------------------------------------
// UBS Talent Accelerator – Quiz Interaction Script
// ------------------------------------------------------------

// Make entire option row clickable
document.querySelectorAll(".quiz-option").forEach(option => {
    option.addEventListener("click", () => {
        const radio = option.querySelector("input[type='radio']");
        if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event("change"));
        }
    });
});

// Highlight selected option (CSS handles the styling)
document.querySelectorAll("input[type='radio']").forEach(radio => {
    radio.addEventListener("change", () => {
        const name = radio.name;

        // Remove highlight from all options in this question
        document.querySelectorAll(`input[name='${name}']`).forEach(r => {
            r.parentElement.classList.remove("selected");
        });

        // Add highlight to the selected option
        radio.parentElement.classList.add("selected");
    });
});

// ------------------------------------------------------------
// Validate before submitting a section
// ------------------------------------------------------------

const form = document.querySelector("form");
if (form) {
    form.addEventListener("submit", event => {
        const questionBlocks = document.querySelectorAll(".quiz-question");
        let firstMissing = null;
        let allAnswered = true;

        questionBlocks.forEach(block => {
            const radios = block.querySelectorAll("input[type='radio']");
            const isAnswered = Array.from(radios).some(r => r.checked);

            if (!isAnswered) {
                allAnswered = false;
                block.classList.add("quiz-question-missing");

                if (!firstMissing) {
                    firstMissing = block;
                }
            } else {
                block.classList.remove("quiz-question-missing");
            }
        });

        if (!allAnswered) {
            event.preventDefault();

            // Scroll to first missing question
            if (firstMissing) {
                firstMissing.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            }
        }
    });
}

// ------------------------------------------------------------
// Smooth scroll for any auto-highlighted missing question
// (Used when server returns validation errors)
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const missing = document.querySelector(".quiz-question-missing");
    if (missing) {
        missing.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }
});

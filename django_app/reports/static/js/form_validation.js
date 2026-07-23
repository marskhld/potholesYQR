document.addEventListener("DOMContentLoaded", function () {
  // Remove validation errors as the user types
  document.querySelectorAll(".form-control").forEach((field) => {
    field.addEventListener("input", function () {
      const error = this.parentElement.querySelector(".error-message");

      if (error && this.value.trim() !== "") {
        error.remove();
        this.classList.remove("error");
      }
    });
  });

  // Description character counter
  const description = document.getElementById("id_description");
  const counter = document.getElementById("description-count");

  if (description && counter) {
    function updateCounter() {
      const count = description.value.length;
      counter.textContent = count;

      if (count >= 500) {
        counter.style.color = "#dc3545"; // red
      } else if (count >= 450) {
        counter.style.color = "#d97706"; // orange
      } else {
        counter.style.color = "#6c757d"; // grey
      }
    }

    updateCounter(); // Set initial count

    description.addEventListener("input", updateCounter);
  }
});

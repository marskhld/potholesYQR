document.querySelectorAll(".form-control").forEach((field) => {
  field.addEventListener("input", function () {
    const error = this.parentElement.querySelector(".error-message");

    if (error && this.value.trim() !== "") {
      error.remove();
      this.classList.remove("error");
    }
  });
});

// if js files grow, then can combine js files for form into one report_form.js file

document.addEventListener("DOMContentLoaded", function () {
  const phoneInput = document.getElementById("id_phone_number");

  if (!phoneInput) return;

  phoneInput.addEventListener("input", function () {
    // Keep only digits
    let digits = this.value.replace(/\D/g, "");

    // Remove leading country code if present
    if (digits.startsWith("1") && digits.length === 11) {
      digits = digits.substring(1);
    }

    // Limit to 10 digits
    digits = digits.substring(0, 10);

    if (digits.length >= 7) {
      this.value = `(${digits.substring(0, 3)}) ${digits.substring(3, 6)}-${digits.substring(6)}`;
    } else if (digits.length >= 4) {
      this.value = `(${digits.substring(0, 3)}) ${digits.substring(3)}`;
    } else if (digits.length > 0) {
      this.value = `(${digits}`;
    }
  });
});

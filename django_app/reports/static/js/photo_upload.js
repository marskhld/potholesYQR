// if js files grow, then can combine js files for form into one report_form.js file

const input = document.getElementById("id_photos");

if (!input) {
  console.error("Photo input not found.");
}

let uploadedPhotos = [];

function displayUploadedPhotos() {
  const photoList = document.getElementById("photo-list");

  photoList.innerHTML = "";

  uploadedPhotos.forEach((file, index) => {
    const fileRow = document.createElement("div");
    fileRow.className = "photo-preview";

    // Image preview
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.alt = file.name;

    // Free temp object URL after loading the image to avoid memory leaks
    img.onload = function () {
      URL.revokeObjectURL(img.src);
    };

    // File name
    const fileName = document.createElement("p");
    fileName.textContent = file.name;

    // Remove button
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Remove";

    removeButton.addEventListener("click", function () {
      removePhoto(index);
    });

    fileRow.appendChild(img);
    fileRow.appendChild(fileName);
    fileRow.appendChild(removeButton);

    photoList.appendChild(fileRow);
  });
}

function removePhoto(index) {
  // Remove photo from array
  uploadedPhotos.splice(index, 1);

  // Rebuild the FileList
  const dataTransfer = new DataTransfer();

  uploadedPhotos.forEach((file) => dataTransfer.items.add(file));

  input.files = dataTransfer.files;

  // Refresh the display
  displayUploadedPhotos();
}

input.addEventListener("change", function () {
  for (const file of this.files) {
    const alreadyAdded = uploadedPhotos.some(
      (existing) =>
        existing.name === file.name &&
        existing.size === file.size &&
        existing.lastModified === file.lastModified,
    );

    if (!alreadyAdded) {
      uploadedPhotos.push(file);
    }
  }

  if (uploadedPhotos.length > 5) {
    alert("You can upload a maximum of 5 photos.");
    uploadedPhotos = uploadedPhotos.slice(0, 5);
  }

  const dataTransfer = new DataTransfer();

  uploadedPhotos.forEach((file) => dataTransfer.items.add(file));

  input.files = dataTransfer.files;

  displayUploadedPhotos();
});

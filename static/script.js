document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("linkForm");

  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission

    const title = document.getElementById("titleInput").value;
    const files = document.getElementById("imageInput").files;
    const duration = document.getElementById("timeInput").value;
    const unit = document.getElementById("timeUnit").value;

    const formData = new FormData();
    formData.append("title", title);
    formData.append("duration", duration);
    formData.append("unit", unit);
    for (let i = 0; i < files.length; i++) {
        formData.append('images', files[i]);
    }

    fetch("/create_link", {
      method: "POST",
      body: formData, // Send the form data
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data); // Handle the response data
        // Additional logic to handle response
      })
      .catch((error) => {
        console.error("Error:", error); // Handle any errors
      });
  });
});

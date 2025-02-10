document.getElementById("saveButtonR").addEventListener("click", async () => {
  saveImage(3);
});

document.getElementById("saveButton").addEventListener("click", async () => {
  saveImage(1);
});

document.getElementById("saveButtonL").addEventListener("click", async () => {
  saveImage(2);
});

function saveImage(screenidx = 1) {
  console.log("Saving image...")

  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    console.log("Queried Tab: " + tabs[0].id)

    console.log("Sending Action: getActiveImage")
    chrome.tabs.sendMessage(tabs[0].id, { action: 'getActiveImage' }, async (response) => {
      const r = response
      console.log("Got Response: ", r)

      if (response && response.src) {
        console.log("Got Response: ", r)

        const imageUrl = r.src
        console.log(imageUrl)


        const dirname = document.getElementById("dirname").value.trim() || "default"; // Fallback to default if empty
        const packname = document.getElementById("packname").value.trim() || "default"; // Fallback to default if empty

        // Check if the URL is an image
        // Fetch the image data
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const filename = (await fetchFilenameFromHeaders(imageUrl)) || getFilenameFromUrl(imageUrl);
        localStorage.setItem("lastpackname", packname);
        localStorage.setItem("lastdirname", dirname);

        // Convert the blob to a base64 string
        const reader = new FileReader();
        reader.onload = async function () {
          const base64Data = reader.result.split(",")[1]; // Remove the data URL prefix

          // Send the data to the backend
          const data = {
            screen: screenidx,
            dirname: dirname,
            packname: packname,
            filename: filename, // Change extension based on actual image type
            content: base64Data,
          };

          const saveResponse = await fetch("http://localhost:5000/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });

          if (saveResponse.ok) {
            const result = await saveResponse.json();
            console.log(result.message);
            alert("Image saved successfully!");
          } else {
            console.error("Failed to save image");
          }
        };

        reader.readAsDataURL(blob); // Read the image blob as a data URL

      }
    })
  });
}


window.onload = () => {
  const lastpackname = localStorage.getItem("lastpackname");
  const lastdirname = localStorage.getItem("lastdirname");
  if (lastpackname) {
    document.getElementById("packname").value = lastpackname;
    document.getElementById("dirname").value = lastdirname;
  }
};

async function fetchFilenameFromHeaders(url) {
  try {
    const response = await fetch(url, { method: "GET" });
    const contentDisposition = response.headers.get("Content-Disposition");
    if (contentDisposition && contentDisposition.includes("filename=")) {
      const matches = contentDisposition.match(/filename="?(.+?)"?$/);
      return matches ? matches[1] : null;
    }
  } catch (error) {
    console.error("Error fetching headers:", error);
  }
  return null; // Fallback if no header or error
}

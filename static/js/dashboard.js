// Upload Image
document.getElementById("uploadBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("imageInput");
    if (fileInput.files.length === 0) return alert("Select an image first");

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    try {
        const res = await axios.post("/api/uploadImage/", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        document.getElementById("uploadResult").innerText = `Image uploaded: ${res.data.img_path}`;
        document.getElementById("imagePathInput").value = res.data.img_path;
    } catch (err) {
        console.error(err);
        alert("Upload failed");
    }
});

// Analyze Image
// Analyze Image
document.getElementById("analyzeBtn").addEventListener("click", async () => {
    const imagePath = document.getElementById("imagePathInput").value;
    if (!imagePath) return alert("Enter image path");

    try {
        // Send as URL-encoded form data
        const params = new URLSearchParams();
        params.append("image_path", imagePath);

        const res = await axios.post(
            "/api/faceDetectionAndBlurAnalysis/",
            params,
            {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
        );

        let html = "";

        // Show message at the top in green
        let message = "";
        if (typeof res.data === "string") {
            message = "Analysis completed"; // fallback message
        } else {
            message = res.data.message || "Analysis completed";
        }
        html += `<p style="color: green; font-weight: bold;">${message}</p>`;

        // Rest of the details
        if (typeof res.data === "string") {
            html += `<p><strong>Image Path:</strong><br><img src="${res.data}" width="300"></p>`;
        } else {
            if (res.data.corrected_image_url) {
                html += `<p><strong>Corrected Image:</strong><br><img src="${res.data.corrected_image_url}" width="300"></p>`;
            }
        }

        document.getElementById("analysisResult").innerHTML = html;

    } catch (err) {
        console.error("Error response:", err.response || err);
        alert("Analysis failed");
    }
});


// Load Previous Evaluations
document.getElementById("loadEvaluationsBtn").addEventListener("click", async () => {
    try {
        const res = await axios.get("/api/getAllDetectionsAndCorrections/");
        const tbody = document.querySelector("#evaluationsTable tbody");
        tbody.innerHTML = "";

        res.data.forEach(ev => {
            // Ensure we have a proper image URL (prepend slash if missing)
            const uploadedImg = ev.image_path.startsWith("/")
                ? ev.image_path
                : "/" + ev.image_path;

            const correctedImg = ev.corrected_image_url
                ? (ev.corrected_image_url.startsWith("/") ? ev.corrected_image_url : "/" + ev.corrected_image_url)
                : null;

            const row = `
                <tr>
                    <td>${ev.id}</td>
                    <td><img src="${uploadedImg}" width="100" alt="Uploaded Image"></td>
                    <td>${ev.is_human_face}</td>
                    <td>${ev.is_blurry}</td>
                    <td>${correctedImg ? `<img src="${correctedImg}" width="100" alt="Corrected Image">` : "N/A"}</td>
                    <td>${new Date(ev.created_on).toLocaleString()}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (err) {
        console.error("Error loading evaluations:", err.response || err);
        alert("Failed to load evaluations");
    }
});


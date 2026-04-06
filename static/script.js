const API = "http://127.0.0.1:5000";

// Upload
async function uploadFile() {
    let file = document.getElementById("fileInput").files[0];

    if (!file) {
        alert("Select file first");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    let res = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
    });

    let data = await res.json();
    document.getElementById("dataPreview").innerHTML = data.html;
}

// Auto Preprocess
async function autoPreprocess() {
    document.getElementById("dataPreview").innerHTML = "Processing...";

    let res = await fetch(`${API}/auto_preprocess`);
    let data = await res.json();

    document.getElementById("dataPreview").innerHTML = data.html;
}

// Visualization
async function visualize() {
    document.getElementById("charts").innerHTML = "Generating charts...";

    let res = await fetch(`${API}/visualize`);
    let data = await res.json();

    let html = "";
    data.images.forEach(img => {
        html += `<img src="${API}/${img}" width="300">`;
    });

    document.getElementById("charts").innerHTML = html;
}

// Download CSV
function download() {
    window.location.href = `${API}/download`;
}

// Download Charts
function downloadCharts() {
    window.location.href = `${API}/download_charts`;
}

function startProgress() {
    let bar = document.getElementById("progressBar");
    let container = document.getElementById("progressContainer");

    container.style.display = "block";
    bar.style.width = "0%";

    let width = 0;
    let interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += 5;
            bar.style.width = width + "%";
        }
    }, 200);

    return interval;
}

function finishProgress(interval) {
    let bar = document.getElementById("progressBar");

    clearInterval(interval);
    bar.style.width = "100%";

    setTimeout(() => {
        document.getElementById("progressContainer").style.display = "none";
    }, 500);
}
async function inspectData() {
    document.getElementById("report").innerHTML = "Generating report...";

    let res = await fetch(`${API}/inspect`);
    let data = await res.json();

    let html = `
        <p><b>Rows:</b> ${data.rows}</p>
        <p><b>Columns:</b> ${data.columns}</p>

        <h3>Columns</h3>
        <p>${data.columns_list.join(", ")}</p>

        <h3>Data Types</h3>
        <ul>
            ${Object.entries(data.dtypes).map(([k,v]) => `<li>${k}: ${v}</li>`).join("")}
        </ul>

        <h3>Missing Values</h3>
        <ul>
            ${Object.entries(data.missing).map(([k,v]) => `<li>${k}: ${v}</li>`).join("")}
        </ul>

        <h3>Statistics</h3>
        ${data.describe}
    `;

    document.getElementById("report").innerHTML = html;
}
function resetSteps() {
    document.querySelectorAll(".step").forEach(step => {
        step.classList.remove("active", "done");
    });
}

function setActive(stepId) {
    document.getElementById(stepId).classList.add("active");
}

function setDone(stepId) {
    let el = document.getElementById(stepId);
    el.classList.remove("active");
    el.classList.add("done");
}
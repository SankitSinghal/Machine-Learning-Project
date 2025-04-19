document.addEventListener("DOMContentLoaded", function () {
    loadGestures("predefined", 1);
    loadGestures("user_defined", 1);
});

function loadGestures(type, page) {
    let url = type === "predefined" ? `/get_predefined_gestures?page=${page}` : `/get_user_defined_gestures?page=${page}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            let tableBody = type === "predefined" ? document.getElementById("predefinedBody") : document.getElementById("userDefinedBody");
            let paginationDiv = type === "predefined" ? document.getElementById("predefined-pagination") : document.getElementById("user-defined-pagination");
            tableBody.innerHTML = "";

            if (data.gestures.length === 0 && type === "user_defined") {
                tableBody.innerHTML = "<tr><td colspan='5' class='text-center'>No user-defined gestures available.</td></tr>";
            }

            data.gestures.forEach((gesture, index) => {
                let row = `<tr>
                    <td>${index + 1}</td>
                    <td><img src="${gesture.image}" class="gesture-img"></td>
                    <td>${gesture.name}</td>
                    <td>${gesture.action}</td>
                    ${type === "user_defined" ? `<td><button class="btn btn-danger btn-sm" onclick="deleteGesture(${gesture.id})">Delete</button></td>` : ""}
                </tr>`;
                tableBody.innerHTML += row;
            });

            renderPagination(paginationDiv, data.total_pages, page, type);
        })
        .catch(error => console.error("Error loading gestures:", error));
}

function renderPagination(container, totalPages, currentPage, type) {
    container.innerHTML = "";
    for (let i = 1; i <= totalPages; i++) {
        let btn = document.createElement("button");
        btn.innerText = i;
        btn.className = `btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline-primary'} mx-1`;
        btn.onclick = () => loadGestures(type, i);
        container.appendChild(btn);
    }
}

function deleteGesture(id) {
    if (!confirm("Are you sure you want to delete this gesture?")) return;
    fetch("/delete_gesture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Gesture deleted successfully.");
            loadGestures("user_defined", 1);
        } else {
            alert("Error deleting gesture.");
        }
    })
    .catch(error => console.error("Error deleting gesture:", error));
}

function toggleSection(type) {
    document.getElementById("predefined-gestures").style.display = type === "predefined" ? "block" : "none";
    document.getElementById("user-defined-gestures").style.display = type === "user-defined" ? "block" : "none";

    // Change button styles
    document.getElementById("predefined-btn").classList.toggle("btn-primary", type === "predefined");
    document.getElementById("predefined-btn").classList.toggle("btn-secondary", type !== "predefined");

    document.getElementById("user-defined-btn").classList.toggle("btn-primary", type === "user-defined");
    document.getElementById("user-defined-btn").classList.toggle("btn-secondary", type !== "user-defined");
}


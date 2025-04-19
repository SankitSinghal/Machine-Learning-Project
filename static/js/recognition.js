document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.getElementById("start-recognition");
    const stopBtn = document.getElementById("stop-recognition");
    const videoSection = document.getElementById("video-section");
    const heroSection = document.getElementById("hero-section");
    const videoFeed = document.getElementById("video-feed");

    let recognitionActive = false;

    // Start Gesture Recognition
    startBtn.addEventListener("click", function () {
        if (!recognitionActive) {
            videoFeed.src = "/recognition_video_feed";
            videoSection.style.display = "block";
            heroSection.style.display = "none";
            recognitionActive = true;
        }
    });

    // Stop Gesture Recognition
    stopBtn.addEventListener("click", function () {
        if (recognitionActive) {
            fetch("/stop_recognition", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "stopped") {
                        videoSection.style.display = "none";
                        heroSection.style.display = "block";
                        videoFeed.src = "";
                        recognitionActive = false;
                        window.location.href = "/";
                    }
                })
                .catch(error => console.error("Error stopping recognition:", error));
        }
    });
});
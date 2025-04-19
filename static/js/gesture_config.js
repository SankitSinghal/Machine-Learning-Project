document.addEventListener("DOMContentLoaded", function () {
    const startButton = document.getElementById("start-button");
    const videoContainer = document.getElementById("video-container");
    const progressBar = document.getElementById("progress_bar");
    const progressText = document.getElementById("progress_text");
    const gestureName = document.getElementById("gesture-name");
    const actionSelect = document.getElementById("gesture-action");
    const parameterContainer = document.getElementById("parameter-container");
    const parameterInput = document.getElementById("gesture-parameter");
    const formContainer = document.getElementById("form-container");
    const completionMessage = document.getElementById("completion-message");
    let videoFeed = document.getElementById("video-feed");

    // Hide progress elements initially
    progressBar.style.display = "none";
    progressText.style.display = "none";
    completionMessage.style.display = "none";

    // Fetch Available Actions from Backend
    async function fetchAvailableActions() {
        try {
            const response = await fetch("/get_available_actions");
            if (!response.ok) throw new Error("Failed to fetch actions");
            const data = await response.json();

            // Clear & Populate Select Options
            actionSelect.innerHTML = "";
            data.available_actions.forEach(action => {
                let option = document.createElement("option");
                option.value = action.name;
                option.textContent = action.name;
                actionSelect.appendChild(option);
            });
        } catch (error) {
            console.error("❌ Error fetching actions:", error);
        }
    }
    fetchAvailableActions();

    //  Show/Hide Parameter Input Based on Selected Action
    actionSelect.addEventListener("change", function () {
        if (actionSelect.value === "Open a Specific File" || actionSelect.value === "Open a Website") {
            parameterContainer.style.display = "block"; // Show input
        } else {
            parameterContainer.style.display = "none"; // Hide input
        }
    });

    // Update Progress Bar Dynamically
    function updateProgress() {
        const eventSource = new EventSource("/progress");

        eventSource.onmessage = function (event) {
            const progress = parseInt(event.data, 10);

            if (progressBar && progressText) {
                progressBar.style.display = "block";
                progressText.style.display = "block";
                progressBar.style.transition = "width 0.5s ease-in-out";
                progressBar.style.width = `${(progress / 600) * 100}%`;
                progressText.innerText = `${progress}/300 Images Collected`;
            }

            if (progress >= 300) {
                eventSource.close();
                showCompletionMessage();
                formContainer.style.display = "block";
                videoContainer.style.display = "none";
                progressBar.style.display = "none";
                progressText.style.display = "none";
            }
        };

        eventSource.onerror = function () {
            console.error("❌ Error in EventSource connection.");
            eventSource.close();
        };
    }

    // Show Completion Message for 3 Seconds, Then Hide It
    function showCompletionMessage() {
        completionMessage.style.display = "block";

        setTimeout(() => {
            completionMessage.style.transition = "opacity 1s ease-in-out";
            completionMessage.style.opacity = "0";

            setTimeout(() => {
                completionMessage.style.display = "none";
                completionMessage.style.opacity = "1";
            }, 1000);
        }, 3000);
    }

    // Ensure Video Feed is Always Loaded
    function loadVideoFeed() {
        if (!videoFeed) {
            videoFeed = document.createElement("img");
            videoFeed.id = "video-feed";
            videoFeed.alt = "Live Video Feed";
            videoFeed.style.width = "100%";
            videoContainer.appendChild(videoFeed);
        }

        videoFeed.src = `/video_feed?timestamp=${new Date().getTime()}`;
        videoFeed.onerror = function () {
            console.warn("⚠️ Video feed failed, retrying...");
            setTimeout(loadVideoFeed, 2000);
        };
    }

    //  Handle Form Submission with Validation
    startButton.addEventListener("click", async function () {
        const gesture = gestureName.value.trim();
        const action = actionSelect.value;
        const parameter = parameterInput.value.trim();

        if (!gesture || !action) {
            alert("⚠️ Gesture name and action are required!");
            return;
        }
        if ((action === "Open a Specific File" || action === "Open a Website") && !parameter) {
            alert("⚠️ Parameter is required!");
            return;
        }

        try {
            const response = await fetch("/start_collection", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ gesture_name: gesture, action: action, parameter: parameter }),
            });

            const data = await response.json();
            if (data.status === "success") {
                formContainer.style.display = "none";
                videoContainer.style.display = "block";
                completionMessage.style.display = "none";
                updateProgress();
                loadVideoFeed();
            } else {
                alert(`${data.message}`);
                formContainer.style.display = "block";
                videoContainer.style.display = "none";
            }
        } catch (error) {
            console.error("❌ Error:", error);
            alert("❌ Something went wrong. Please try again.");
        }
    });

});

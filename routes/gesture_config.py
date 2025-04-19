import cv2
import numpy as np
import os
import time
import threading
import sqlite3
from flask import Blueprint, Response, request, jsonify, render_template, stream_with_context
from cvzone.HandTrackingModule import HandDetector
from .model import train_gesture_model

bp = Blueprint("gesture_config", __name__)

DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dataset/user_defined/"))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/gestures.db"))
detector = HandDetector(maxHands=1)

imgSize = 300
offset = 15
max_images = 300
video_feed_active = False
image_count = 0
cap = None

USER_DEFINED_ACTIONS = [
    "No Action", "Close Application", "Minimize/Maximize Window", "Take Screenshot", "Open a Specific File",
    "Search for a File", "Move File", "Delete File", "Open a Website", "Google Search",
    "Open YouTube & Play Music", "Next/Previous Track", "Copy", "Cut", "Paste", "Undo", "Redo",
    "Lock Screen", "Open Task Manager"
]

@bp.route('/gesture_config')
def gesture_config_page():
    """Render the gesture configuration page."""
    return render_template("gesture_config.html")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def save_to_database(gesture_name, action, parameter):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            reusable = 1 if action in ["No Action", "Open a Specific File", "Open a Website"] else 0
            cursor.execute(
                "INSERT INTO gestures (name, type, reusable, action, parameter) VALUES (?, 'user_defined', ?, ?, ?)",
                (gesture_name, reusable, action, parameter))
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def collect_gesture_images(gesture_name, action, parameter):
    global video_feed_active, image_count, cap
    video_feed_active = True
    image_count = 0

    folder_path = os.path.join(DATASET_PATH, gesture_name)
    display_image_path = os.path.join(os.path.dirname(__file__), "../static/images/user_defined/")
    display_image_file = os.path.join(display_image_path, f"{gesture_name}.jpg")
    os.makedirs(folder_path, exist_ok=True)

    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        time.sleep(5)

    saved_display_image = False

    while image_count < max_images and video_feed_active:
        success, img = cap.read()
        if not success:
            continue

        hands, img = detector.findHands(img)
        if hands:
            x, y, w, h = hands[0]['bbox']
            x, y, w, h = max(0, x - offset), max(0, y - offset), w + (2 * offset), h + (2 * offset)

            imgCrop = img[y:y+h, x:x+w]
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

            if imgCrop.size != 0:
                aspect_ratio = h / w
                if aspect_ratio > 1:
                    new_h, new_w = imgSize, int((imgSize / h) * w)
                else:
                    new_w, new_h = imgSize, int((imgSize / w) * h)

                imgResize = cv2.resize(imgCrop, (new_w, new_h))
                y_offset, x_offset = (imgSize - new_h) // 2, (imgSize - new_w) // 2
                imgWhite[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = imgResize

                cv2.imwrite(f"{folder_path}/Image_{image_count}.jpg", imgWhite)
                image_count += 1

                if image_count==120 and (not saved_display_image):
                    cv2.imwrite(display_image_file, imgWhite)
                    saved_display_image = True

        time.sleep(0.1)

    video_feed_active = False
    save_to_database(gesture_name, action, parameter)
    threading.Thread(target=train_gesture_model).start()
    if cap is not None:
        cap.release()  # Release camera
        cap = None  # Reset cap to None
    cv2.destroyAllWindows()
    cv2.waitKey(1)  # Ensures OpenCV windows close properly

@bp.route('/progress')
def progress():
    def generate():
        while image_count < max_images:
            yield f"data:{image_count}\n\n"
            time.sleep(0.2)
        yield f"data:300\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@bp.route('/video_feed')
def video_feed():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)

    def generate():
        while video_feed_active:
            success, frame = cap.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/start_collection', methods=['POST'])
def start_collection():
    global video_feed_active
    video_feed_active = True
    data = request.json
    gesture_name, action, parameter = data.get("gesture_name"), data.get("action"), data.get("parameter")

    if not gesture_name or not action:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400
    if action in ["Open a Specific File", "Open a Website"] and not parameter:
        return jsonify({"status": "error", "message": "Parameter is required!"}), 400

    # Check if gesture name already exists in the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gestures WHERE name = ?", (gesture_name,))
    count = cursor.fetchone()[0]
    conn.close()

    if count > 0:
        return jsonify({"status": "error", "message": "❌ Gesture name already exists! Choose a different one."}), 400

    threading.Thread(target=collect_gesture_images, args=(gesture_name, action, parameter)).start()
    return jsonify({"status": "success"})

def get_existing_gestures():
    """Fetch all existing gestures from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT action FROM gestures WHERE reusable=0")
        existing_gestures = {row[0] for row in cursor.fetchall()}
    return existing_gestures

@bp.route('/get_available_actions')
def get_available_actions():
    try:
        existing_gestures = get_existing_gestures()

        available_gestures = [
            {"name": action} for action in USER_DEFINED_ACTIONS if action not in existing_gestures
        ]

        return jsonify({"available_actions": available_gestures})

    except Exception as e:
        print(f"Error fetching gestures: {e}")
        return jsonify({"error": "Failed to fetch gestures"}), 500

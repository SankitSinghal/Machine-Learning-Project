import cv2
import numpy as np
import tensorflow as tf
import pickle
from flask import Blueprint, render_template, Response, jsonify
from cvzone.HandTrackingModule import HandDetector
from collections import deque
from .execute_action import execute_gesture_action
from .mouse import process_frame

bp = Blueprint('recognition', __name__)

# Load Model & Encoder
model = tf.keras.models.load_model("models/gesture_model.h5")
with open("models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Initialize Hand Detector
detector = HandDetector(maxHands=1)
imgSize = 64
offset = 15
confidence_threshold = 0.7
prediction_smoothing = deque(maxlen=5)


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            continue

        hands, img = detector.findHands(img)
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            # Crop & Resize Image for Model Input
            y1, y2 = max(0, y - offset), min(img.shape[0], y + h + offset)
            x1, x2 = max(0, x - offset), min(img.shape[1], x + w + offset)
            imgCrop = img[y1:y2, x1:x2]

            aspect_ratio = h / w
            if aspect_ratio > 1:
                scale = imgSize / h
                w_new = int(scale * w)
                imgResize = cv2.resize(imgCrop, (w_new, imgSize))
                w_gap = (imgSize - w_new) // 2
                imgWhite[:, w_gap:w_gap + w_new] = imgResize
            else:
                scale = imgSize / w
                h_new = int(scale * h)
                imgResize = cv2.resize(imgCrop, (imgSize, h_new))
                h_gap = (imgSize - h_new) // 2
                imgWhite[h_gap:h_gap + h_new, :] = imgResize

            # Process Image for Model
            imgGray = cv2.cvtColor(imgWhite, cv2.COLOR_BGR2GRAY) / 255.0
            imgGray = np.expand_dims(imgGray, axis=(0, -1))

            predictions = model.predict(imgGray)[0]
            confidence = np.max(predictions)
            pred_label = label_encoder.inverse_transform([np.argmax(predictions)])[0]

            if confidence > confidence_threshold:
                prediction_smoothing.append(pred_label)

            if prediction_smoothing:
                stable_prediction = max(set(prediction_smoothing), key=prediction_smoothing.count)
            else:
                stable_prediction = "Unknown"

            cv2.putText(img, f"Gesture: {stable_prediction}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            print(stable_prediction)
            if stable_prediction in ["victory_sign","victory_with_thumb"]:
                process_frame(img)
            else:
                execute_gesture_action(stable_prediction)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


@bp.route("/recognition")
def recognition_page():
    return render_template("recognition.html")


@bp.route("/recognition_video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    global recognition_active
    recognition_active = False
    cv2.destroyAllWindows()
    return jsonify({"status": "stopped"})

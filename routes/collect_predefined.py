import cv2
import numpy as np
import os
import time
import sqlite3
from cvzone.HandTrackingModule import HandDetector

# Predefined gestures and their corresponding actions
PREDEFINED_GESTURES = {
    "victory_sign": "Move Mouse",
    "victory_with_thumb":"Stop Mouse",
    "one_finger_up": "Left Click",
    "fist": "Right Click",
    "open_palm": "Play/Pause Media",
    "thumbs_up": "Volume Up",
    "thumbs_down": "Volume Down",
    "point_right": "Next Slide",
    "point_left": "Previous Slide"
}

# Paths
DATASET_PATH = "../dataset/predefined/"
DB_PATH = "../database/gestures.db"

# Ensure dataset directory exists
os.makedirs(DATASET_PATH, exist_ok=True)

# Initialize webcam and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

imgSize = 300
offset = 15
max_images = 300  # Total images per gesture

def save_to_database(gesture_name):
    """ Saves completed gesture to the database """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insert into gestures table
        cursor.execute("INSERT INTO gestures (name, type) VALUES (?, 'predefined')", (gesture_name,))
        gesture_id = cursor.lastrowid

        # Insert into gesture_actions table
        cursor.execute("INSERT INTO gesture_actions (gesture_id, action) VALUES (?, ?)",
                       (gesture_id, PREDEFINED_GESTURES[gesture_name]))

        conn.commit()
        conn.close()
        print(f"✅ Data collection complete for {gesture_name}. Saved to database.")

    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")

def collect_gesture_images(gesture_name):
    """ Collects 300 images for the given gesture """
    folder_path = os.path.join(DATASET_PATH, gesture_name)
    os.makedirs(folder_path, exist_ok=True)

    count = 0
    while count < max_images:
        success, img = cap.read()
        if not success:
            continue

        hands, img = detector.findHands(img)
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            y1, y2 = max(0, y - offset), min(img.shape[0], y + h + offset)
            x1, x2 = max(0, x - offset), min(img.shape[1], x + w + offset)

            imgCrop = img[y1:y2, x1:x2]

            ratio = h / w
            if ratio > 1:
                k = imgSize / h
                w_new = int(k * w)
                imgResize = cv2.resize(imgCrop, (w_new, imgSize))
                w_gap = (imgSize - w_new) // 2
                imgWhite[:, w_gap:w_gap + w_new] = imgResize
            else:
                k = imgSize / w
                h_new = int(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, h_new))
                h_gap = (imgSize - h_new) // 2
                imgWhite[h_gap:h_gap + h_new, :] = imgResize

            cv2.imwrite(f"{folder_path}/Image_{time.time()}.jpg", imgWhite)
            count += 1
            print(f"📸 Capturing {gesture_name}: {count}/{max_images}")

        cv2.imshow("Webcam Feed", img)
        cv2.waitKey(1)

    save_to_database(gesture_name)

print("🎥 Video feed started. Press 'S' to collect data for gestures.")
print("🔴 Press 'Q' anytime to quit.")

gesture_list = list(PREDEFINED_GESTURES.keys())  # Convert to list for indexing
index = 0  # Start with the first gesture

while True:
    success, img = cap.read()
    if not success:
        continue

    hands, img = detector.findHands(img)
    cv2.imshow("Webcam Feed", img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and index < len(gesture_list):
        gesture_name = gesture_list[index]
        print(f"🟢 Collecting data for: {gesture_name}...")
        collect_gesture_images(gesture_name)
        index += 1  # Move to the next gesture

        if index < len(gesture_list):
            print("✅ Data collection complete. Press 'S' to start next gesture.")
        else:
            print("🎉 All predefined gestures collected! Press 'Q' to quit.")

    elif key == ord('q'):
        print("🔴 Exiting program.")
        break

cap.release()
cv2.destroyAllWindows()

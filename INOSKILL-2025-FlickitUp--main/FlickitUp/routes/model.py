import os
import cv2
import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder


def train_gesture_model():
    PREDEFINED_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dataset/predefined/"))
    USER_DEFINED_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dataset/user_defined/"))
    MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/gesture_model.h5"))
    ENCODER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/label_encoder.pkl"))
    IMG_SIZE = 64

    X, y = [], []
    gesture_labels = []

    for dataset_type in [PREDEFINED_PATH, USER_DEFINED_PATH]:
        if not os.path.exists(dataset_type):
            print(f"⚠️ Directory not found: {dataset_type}")
            continue

        for gesture_name in os.listdir(dataset_type):
            folder_path = os.path.join(dataset_type, gesture_name)
            if not os.path.isdir(folder_path):
                continue

            print(f"📂 Processing gesture: {gesture_name}")

            if gesture_name not in gesture_labels:
                gesture_labels.append(gesture_name)

            for img_name in os.listdir(folder_path):
                img_path = os.path.join(folder_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"⚠️ Skipping invalid image: {img_path}")
                    continue

                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)) / 255.0
                X.append(img)
                y.append(gesture_name)

    X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    y = np.array(y)

    if len(X) == 0 or len(y) == 0:
        raise ValueError("❌ No images found! Ensure dataset directories contain valid images.")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    y_categorical = to_categorical(y_encoded, num_classes=len(gesture_labels))

    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(le, f)

    print(f"🟢 Unique Gesture Labels: {gesture_labels}")
    print(f"🟢 Total Samples: {len(X)}, Shape: {X.shape}")
    print(f"🟢 Total Labels: {len(y_categorical)}, Shape: {y_categorical.shape}")

    model = Sequential([
        Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(len(gesture_labels), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X, y_categorical, epochs=10, validation_split=0.2)
    model.save(MODEL_PATH)
    print("✅ Model trained & saved successfully!")
import cv2
import mediapipe as mp
import pyautogui
import random
import numpy as np
from pynput.mouse import Button, Controller

mouse = Controller()

screen_width, screen_height = pyautogui.size()

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    return np.abs(np.degrees(radians))

def get_distance(p1, p2):
    return np.hypot(p2[0] - p1[0], p2[1] - p1[1])

def find_finger_tip(hand_landmarks):
    index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return (index_finger_tip.x, index_finger_tip.y)

prev_x, prev_y = 0, 0
smooth_factor = 0.5


def move_mouse(index_finger_tip):
    global prev_x, prev_y

    if index_finger_tip:
        x = int(index_finger_tip[0] * screen_width)
        y = int(index_finger_tip[1] * screen_height)

        smoothed_x = int(prev_x * (1 - smooth_factor) + x * smooth_factor)
        smoothed_y = int(prev_y * (1 - smooth_factor) + y * smooth_factor)
        pyautogui.moveTo(smoothed_x, smoothed_y)
        prev_x, prev_y = smoothed_x, smoothed_y


def detect_gesture(frame, hand_landmarks):
    if hand_landmarks:
        landmark_list = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
        thumb_index_dist = get_distance(landmark_list[4], landmark_list[5])
        move_mouse(find_finger_tip(hand_landmarks))

def process_frame(frame):
    draw = mp.solutions.drawing_utils
    frame = cv2.flip(frame, 1)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    processed = hands.process(frameRGB)

    if processed.multi_hand_landmarks:
        for hand_landmarks in processed.multi_hand_landmarks:
            draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
            detect_gesture(frame, hand_landmarks)

    return frame

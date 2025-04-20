import os
import webbrowser
import keyboard
import sqlite3
import pyautogui
import time

# Path to gesture database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/gestures.db"))

def get_gesture_action(gesture_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action, parameter FROM gestures WHERE name = ?", (gesture_name,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
        return None, None


def execute_gesture_action(gesture_name):
    """Execute the action associated with the recognized gesture."""
    action, parameter = get_gesture_action(gesture_name)
    if not action or action == "No Action":
        print(f"⚠️ No action assigned for gesture: {gesture_name}")
        return

    print(f"🟢 Executing {gesture_name}: {action} ({parameter if parameter else 'No Parameter'})")
    try:
        if action == "Left Click":
            pyautogui.click()
        elif action == "Right Click":
            pyautogui.rightClick()
        elif action == "Play/Pause Media":
            keyboard.press_and_release("space")
        elif action == "Volume Up":
            keyboard.press_and_release("volume up")
        elif action == "Volume Down":
            keyboard.press_and_release("volume down")
        elif action == "Next Slide":
            keyboard.press_and_release("right")
        elif action == "Previous Slide":
            keyboard.press_and_release("left")
        elif action == "Close Application":
            keyboard.press_and_release("alt + f4")
        elif action == "Minimize/Maximize Window":
            keyboard.press_and_release("win + d")
        elif action == "Take Screenshot":
            keyboard.press_and_release("win + prtsc")
        elif action == "Open a Specific File":
            os.startfile(parameter) if parameter else print("⚠️ No file path specified.")
        elif action == "Search for a File":
            os.system(f"explorer search-ms:query={parameter}") if parameter else print("⚠️ No search query specified.")
        elif action == "Move File":
            os.rename(parameter.split('|')[0], parameter.split('|')[1]) if parameter else print(
                "⚠️ Invalid move parameters.")
        elif action == "Delete File":
            os.remove(parameter) if parameter else print("⚠️ No file specified to delete.")
        elif action == "Open a Website":
            webbrowser.open(parameter) if parameter else print("⚠️ No URL specified.")
        elif action == "Google Search":
            webbrowser.open(f"https://www.google.com/search?q={parameter}") if parameter else print(
                "⚠️ No search query specified.")
        elif action == "Open YouTube & Play Music":
            webbrowser.open(f"https://www.youtube.com/results?search_query={parameter}") if parameter else print(
                "⚠️ No song name specified.")
        elif action == "Next/Previous Track":
            keyboard.press_and_release("media next" if parameter == "next" else "media previous")
        elif action == "Copy":
            keyboard.press_and_release("ctrl + c")
        elif action == "Cut":
            keyboard.press_and_release("ctrl + x")
        elif action == "Paste":
            keyboard.press_and_release("ctrl + v")
        elif action == "Undo":
            keyboard.press_and_release("ctrl + z")
        elif action == "Redo":
            keyboard.press_and_release("ctrl + y")
        elif action == "Lock Screen":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif action == "Open Task Manager":
            keyboard.press_and_release("ctrl + shift + esc")
        else:
            print(f"⚠️ Unrecognized action: {action}")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

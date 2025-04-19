import sqlite3
import os

def initialize_db():
    db_path = os.path.join(os.path.dirname(__file__), "gestures.db")  # Ensures correct path

    if not os.path.exists(db_path):
        print("Creating gestures.db...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table for storing gestures
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gestures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT CHECK(type IN ('predefined', 'user_defined')) NOT NULL,
            reusable INTEGER NOT NULL DEFAULT 0 CHECK(reusable IN (0, 1)),
            action TEXT NOT NULL,
            parameter TEXT  -- Stores file path, URL, or any extra input (NULL if not needed)
        )
    ''')

    PREDEFINED_GESTURES = {
        "victory_sign": "Move Mouse",
        "victory_with_thumb": "Stop Mouse",
        "one_finger_up": "Left Click",
        "fist": "Right Click",
        "open_palm": "Play/Pause Media",
        "thumbs_up": "Volume Up",
        "thumbs_down": "Volume Down",
        "point_right": "Next Slide",
        "point_left": "Previous Slide"
    }

    for gesture, action in PREDEFINED_GESTURES.items():
        cursor.execute(
            "INSERT INTO gestures (name, type, reusable, action, parameter) VALUES (?, 'predefined', 0, ?, NULL)",
            (gesture, action)
        )
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_db()

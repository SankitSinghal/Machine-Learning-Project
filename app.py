from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database/gestures.db')
    conn.row_factory = sqlite3.Row  # To return results as dictionaries
    return conn

# Registering routes (importing later to avoid circular imports)
from routes import index, recognition, gestures, gesture_config

app.register_blueprint(index.bp)
app.register_blueprint(recognition.bp)
app.register_blueprint(gestures.bp)
app.register_blueprint(gesture_config.bp)

# Running the app
if __name__ == '__main__':
    app.run(debug=True)

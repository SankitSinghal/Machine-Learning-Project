from flask import Flask, render_template
import sqlite3
from routes import index, recognition, gestures, gesture_config
import os

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database/gestures.db')
    conn.row_factory = sqlite3.Row
    return conn

app.register_blueprint(index.bp)
app.register_blueprint(recognition.bp)
app.register_blueprint(gestures.bp)
app.register_blueprint(gesture_config.bp)

# Running the app
if __name__ == '__main__':
    app.run(debug=True)

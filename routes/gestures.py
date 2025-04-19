from flask import Blueprint, render_template, jsonify, request
import sqlite3
import os
import shutil
import threading
from .model import train_gesture_model

# Define Blueprint
bp = Blueprint('gestures', __name__)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/gestures.db"))
image_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/images"))
dataset_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dataset/user_defined"))

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# Route to render the gestures management page
@bp.route('/gestures')
def gestures_page():
    return render_template('gestures.html')


# Route to fetch paginated predefined gestures
@bp.route('/get_predefined_gestures', methods=['GET'])
def get_predefined_gestures():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gestures WHERE type = 'predefined' LIMIT ? OFFSET ?", (limit, offset))
    gestures = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM gestures WHERE type = 'predefined'")
    total = cursor.fetchone()[0]
    conn.close()

    data = [{
        'id': g['id'],
        'name': g['name'],
        'action': g['action'],
        'image': f"/static/images/predefined/{g['name']}.jpg"
    } for g in gestures]

    return jsonify({'gestures': data, 'total_pages': (total // limit) + (1 if total % limit else 0)})


# Route to fetch paginated user-defined gestures
@bp.route('/get_user_defined_gestures', methods=['GET'])
def get_user_defined_gestures():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gestures WHERE type = 'user_defined' LIMIT ? OFFSET ?", (limit, offset))
    gestures = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM gestures WHERE type = 'user_defined'")
    total = cursor.fetchone()[0]
    conn.close()

    if not gestures:
        return jsonify({'message': 'No user-defined gestures available', 'gestures': [], 'total_pages': 0})

    data = [{
        'id': g['id'],
        'name': g['name'],
        'action': g['action'],
        'image': f"/static/images/user_defined/{g['name']}.jpg"
    } for g in gestures]

    return jsonify({'gestures': data, 'total_pages': (total // limit) + (1 if total % limit else 0)})



# Route to delete a user-defined gesture
@bp.route('/delete_gesture', methods=['POST'])
def delete_gesture():
    gesture_id = request.json.get('id')
    if not gesture_id:
        return jsonify({'error': 'Invalid gesture ID'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM gestures WHERE id = ? AND type = 'user_defined'", (gesture_id,))
    gesture = cursor.fetchone()

    if gesture:
        gesture_name = gesture['name']
        image_path = os.path.join(image_base_path, 'user_defined', f"{gesture_name}.jpg")
        dataset_path = os.path.join(dataset_base_path, gesture_name)

        # Delete the gesture image
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete all 300 images in dataset folder
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)  # Deletes the entire directory

        # Delete gesture from the database
        cursor.execute("DELETE FROM gestures WHERE id = ?", (gesture_id,))
        conn.commit()
        conn.close()

        # Update the gesture model
        threading.Thread(target=train_gesture_model).start()

        return jsonify({'success': True})
    else:
        conn.close()
        return jsonify({'error': 'Gesture not found'}), 404

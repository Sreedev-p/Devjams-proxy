from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid

app = Flask(__name__)
# Crucial for Hackathons: Allow all teammates' IP addresses to talk to this API
CORS(app) 

DB_FILE = 'company_database.db'

def init_db():
    """Creates the vulnerable database table when the server boots."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                user_name TEXT,
                sensitive_data TEXT
            )
        ''')
init_db()

@app.route('/api/records', methods=['POST'])
def create_record():
    """Receives data (which will be ciphertext from the proxy) and saves it."""
    data = request.json
    
    # We generate a unique ID for the database row
    record_id = str(uuid.uuid4())
    user_name = data.get('user_name', 'Unknown')
    
    # This is the field the proxy will secretly encrypt before it reaches here
    sensitive_data = data.get('sensitive_data', '')

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            'INSERT INTO records (id, user_name, sensitive_data) VALUES (?, ?, ?)',
            (record_id, user_name, sensitive_data)
        )
    
    return jsonify({"status": "success", "id": record_id}), 201


@app.route('/api/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """Returns a specific record to the proxy/frontend."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM records WHERE id = ?', (record_id,))
        row = cursor.fetchone()

    if row:
        return jsonify(dict(row)), 200
    
    return jsonify({"error": "Record not found"}), 404


@app.route('/api/records', methods=['GET'])
def get_all_records():
    """Returns EVERYTHING. Perfect for powering the 'Hacker View' on the frontend."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM records')
        rows = cursor.fetchall()
        
    return jsonify([dict(row) for row in rows]), 200

if __name__ == '__main__':
    # 0.0.0.0 exposes this server to your local Wi-Fi network
    print("Starting Target Enterprise Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
Webhook API
===========
Flask API to receive webhook notifications from automated workflows.
"""

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import json
import os

app = Flask(__name__)

DB_PATH = "/app/data/prism.db"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "prism-webhook-2026")  # Change this!


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_webhook_db():
    """Initialize webhook messages table."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            severity TEXT,
            message TEXT,
            payload TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "prism-webhook"}), 200


@app.route('/webhook/receive', methods=['POST'])
def receive_webhook():
    """
    Receive webhook POST requests.
    
    Expected JSON payload:
    {
        "secret": "prism-webhook-2026",
        "source": "GCP Workflow",
        "severity": "info|warning|error|critical",
        "message": "Your message here",
        "data": {...}  // Optional additional data
    }
    """
    try:
        # Verify content type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        payload = request.get_json()
        
        # Validate secret
        if payload.get('secret') != WEBHOOK_SECRET:
            return jsonify({"error": "Invalid secret"}), 401
        
        # Extract fields
        source = payload.get('source', 'Unknown')
        severity = payload.get('severity', 'info').lower()
        message = payload.get('message', '')
        data = payload.get('data', {})
        
        # Validate severity
        if severity not in ['info', 'warning', 'error', 'critical']:
            severity = 'info'
        
        # Store in database
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO webhook_messages (source, severity, message, payload)
            VALUES (?, ?, ?, ?)
        """, (source, severity, message, json.dumps(data)))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Webhook received",
            "id": message_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/stats', methods=['GET'])
def webhook_stats():
    """Get webhook statistics."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM webhook_messages")
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM webhook_messages 
            GROUP BY severity
        """)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            "total_messages": total,
            "by_severity": by_severity
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_webhook_db()
    # Run on port 5000, accessible from outside the container
    app.run(host='0.0.0.0', port=5000, debug=False)

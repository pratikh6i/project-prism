"""
Project Prism - SQLite Database Handler
========================================
Manages clients, client details, documents, and settings.
"""

import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd

from utils.logger import logger

DB_PATH = "/app/data/prism.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database with all required tables."""
    logger.info("Initializing database...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            gcp_project_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Client details (for manual notes/data per client)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    
    # Documents for Ops Wiki
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            doc_url TEXT NOT NULL,
            doc_type TEXT DEFAULT 'google_doc',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # App settings (theme, etc)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Initialize default theme
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'light')
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized!")


# ============ CLIENT FUNCTIONS ============

def add_client(name: str, project_id: str) -> tuple[bool, str]:
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO clients (client_name, gcp_project_id) VALUES (?, ?)",
            (name.strip(), project_id.strip())
        )
        conn.commit()
        return True, f"Client '{name}' added!"
    except sqlite3.IntegrityError:
        return False, f"Project ID '{project_id}' already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_clients() -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT id, client_name, gcp_project_id, created_at FROM clients ORDER BY created_at DESC",
            conn
        )
        return df
    except:
        return pd.DataFrame(columns=['id', 'client_name', 'gcp_project_id', 'created_at'])
    finally:
        conn.close()


def get_client_by_id(client_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()


def delete_client(client_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ============ CLIENT DETAILS FUNCTIONS ============

def get_client_details(client_id: int) -> dict:
    """Get all details for a client as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT field_name, field_value FROM client_details WHERE client_id = ?",
            (client_id,)
        )
        return {row['field_name']: row['field_value'] for row in cursor.fetchall()}
    finally:
        conn.close()


def save_client_detail(client_id: int, field_name: str, field_value: str) -> bool:
    """Save or update a client detail field."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO client_details (client_id, field_name, field_value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(client_id, field_name) DO UPDATE SET
                field_value = excluded.field_value,
                updated_at = CURRENT_TIMESTAMP
        """, (client_id, field_name, field_value))
        conn.commit()
        return True
    except:
        # If unique constraint doesn't exist, use old method
        cursor.execute("DELETE FROM client_details WHERE client_id = ? AND field_name = ?", (client_id, field_name))
        cursor.execute(
            "INSERT INTO client_details (client_id, field_name, field_value) VALUES (?, ?, ?)",
            (client_id, field_name, field_value)
        )
        conn.commit()
        return True
    finally:
        conn.close()


# ============ DOCUMENT FUNCTIONS ============

def add_document(title: str, url: str, doc_type: str = 'google_doc') -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO documents (title, doc_url, doc_type) VALUES (?, ?, ?)",
            (title.strip(), url.strip(), doc_type)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_documents() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM documents ORDER BY created_at DESC", conn)
    except:
        return pd.DataFrame(columns=['id', 'title', 'doc_url', 'doc_type', 'created_at'])
    finally:
        conn.close()


def delete_document(doc_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ============ SETTINGS FUNCTIONS ============

def get_setting(key: str, default: str = None) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    finally:
        conn.close()


def set_setting(key: str, value: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()
        return True
    finally:
        conn.close()

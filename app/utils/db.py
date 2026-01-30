"""
Project Prism - SQLite Database Handler
========================================
Manages client configurations with persistent storage.
Database file: /app/data/prism.db
"""

import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd

from utils.logger import logger

# Configuration
DB_PATH = "/app/data/prism.db"


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with row factory enabled.
    
    Returns:
        sqlite3.Connection instance
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize the database and create tables if they don't exist.
    """
    logger.info("Initializing database...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            gcp_project_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    logger.info("Database initialized successfully!")


def add_client(name: str, project_id: str) -> tuple[bool, str]:
    """
    Add a new client to the database.
    
    Args:
        name: Client name
        project_id: GCP Project ID (must be unique)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    logger.info(f"Adding client: {name} with project ID: {project_id}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO clients (client_name, gcp_project_id) VALUES (?, ?)",
            (name.strip(), project_id.strip())
        )
        conn.commit()
        logger.info(f"Client '{name}' added successfully!")
        return True, f"Client '{name}' added successfully!"
    
    except sqlite3.IntegrityError:
        error_msg = f"A client with project ID '{project_id}' already exists."
        logger.warning(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Error adding client: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    finally:
        conn.close()


def get_clients() -> pd.DataFrame:
    """
    Retrieve all clients from the database.
    
    Returns:
        Pandas DataFrame with all client records
    """
    logger.debug("Fetching all clients from database...")
    
    conn = get_connection()
    
    try:
        df = pd.read_sql_query(
            "SELECT id, client_name, gcp_project_id, created_at FROM clients ORDER BY created_at DESC",
            conn
        )
        logger.debug(f"Retrieved {len(df)} clients")
        return df
    
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        return pd.DataFrame(columns=['id', 'client_name', 'gcp_project_id', 'created_at'])
    
    finally:
        conn.close()


def delete_client(client_id: int) -> tuple[bool, str]:
    """
    Delete a client by ID.
    
    Args:
        client_id: The client's database ID
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    logger.info(f"Deleting client with ID: {client_id}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if client exists
        cursor.execute("SELECT client_name FROM clients WHERE id = ?", (client_id,))
        result = cursor.fetchone()
        
        if not result:
            error_msg = f"Client with ID {client_id} not found."
            logger.warning(error_msg)
            return False, error_msg
        
        client_name = result['client_name']
        
        # Delete the client
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        
        success_msg = f"Client '{client_name}' deleted successfully!"
        logger.info(success_msg)
        return True, success_msg
    
    except Exception as e:
        error_msg = f"Error deleting client: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    finally:
        conn.close()


def get_client_by_id(client_id: int) -> Optional[dict]:
    """
    Get a single client by ID.
    
    Args:
        client_id: The client's database ID
    
    Returns:
        Dictionary with client data or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, client_name, gcp_project_id, created_at FROM clients WHERE id = ?",
            (client_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return None
    
    finally:
        conn.close()

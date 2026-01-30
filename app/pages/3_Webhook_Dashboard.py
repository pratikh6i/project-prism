"""
Webhook Dashboard
=================
View webhook messages with support for tables, lists, code, and custom content.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_setting, get_connection
from utils.logger import logger

st.set_page_config(page_title="Webhooks | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
is_dark = theme == 'dark'

if is_dark:
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3, th, td { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
    </style>""", unsafe_allow_html=True)


def migrate_webhook_table():
    """Migrate old webhook table to new schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if old columns exist
    cursor.execute("PRAGMA table_info(webhook_messages)")
    columns = {row[1] for row in cursor.fetchall()}
    
    # If old schema, migrate
    if 'message' in columns and 'content' not in columns:
        logger.info("Migrating webhook_messages table to new schema...")
        
        # Rename old table
        cursor.execute("ALTER TABLE webhook_messages RENAME TO webhook_messages_old")
        
        # Create new table
        cursor.execute("""
            CREATE TABLE webhook_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                severity TEXT,
                message_type TEXT DEFAULT 'text',
                title TEXT,
                content TEXT,
                payload TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migrate data
        cursor.execute("""
            INSERT INTO webhook_messages (id, source, severity, message_type, title, content, payload, received_at)
            SELECT id, source, severity, 'text', '', message, payload, received_at
            FROM webhook_messages_old
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE webhook_messages_old")
        
        conn.commit()
        logger.info("Migration complete!")
    
    conn.close()


def get_webhook_messages(limit=100, severity_filter=None, source_filter=None):
    """Fetch webhook messages from database."""
    # Ensure schema is up to date
    migrate_webhook_table()
    
    conn = get_connection()
    
    query = "SELECT * FROM webhook_messages WHERE 1=1"
    params = []
    
    if severity_filter and severity_filter != "All":
        query += " AND severity = ?"
        params.append(severity_filter.lower())
    
    if source_filter and source_filter != "All":
        query += " AND source = ?"
        params.append(source_filter)
    
    query += " ORDER BY received_at DESC LIMIT ?"
    params.append(limit)
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Error fetching webhook messages: {e}")
        conn.close()
        return pd.DataFrame()


def get_sources():
    """Get unique sources."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT source FROM webhook_messages ORDER BY source")
        sources = [row[0] for row in cursor.fetchall()]
    except:
        sources = []
    conn.close()
    return sources


def delete_message(msg_id):
    """Delete a webhook message."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM webhook_messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()


def render_message_content(row, is_dark):
    """Render message content based on type."""
    # Handle missing columns gracefully
    content_type = row.get('message_type', 'text') if 'message_type' in row else 'text'
    content = row.get('content', '') if 'content' in row else row.get('message', '')
    title = row.get('title', '') if 'title' in row else ''
    
    # Title if present
    if title:
        st.markdown(f"**{title}**")
    
    # Render based on type
    if content_type == 'table':
        try:
            table_data = json.loads(content) if isinstance(content, str) else content
            headers = table_data.get('headers', [])
            rows = table_data.get('rows', [])
            
            if headers and rows:
                df = pd.DataFrame(rows, columns=headers)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.text(content)
        except Exception as e:
            logger.error(f"Error rendering table: {e}")
            st.text(content)
    
    elif content_type == 'list':
        try:
            items = json.loads(content) if isinstance(content, str) else content
            if isinstance(items, list):
                for item in items:
                    st.markdown(f"• {item}")
            else:
                st.text(content)
        except Exception as e:
            logger.error(f"Error rendering list: {e}")
            st.text(content)
    
    elif content_type == 'code':
        st.code(content, language='text')
    
    elif content_type == 'json':
        try:
            json_data = json.loads(content) if isinstance(content, str) else content
            st.json(json_data)
        except Exception as e:
            logger.error(f"Error rendering JSON: {e}")
            st.code(content, language='json')
    
    else:  # text
        st.markdown(content)


st.title("📡 Webhook Dashboard")
st.markdown("View incoming webhook messages from your automated workflows")

st.divider()

# Webhook URL info
st.markdown("##### Webhook Endpoint")
vm_ip = "35.200.238.102"
webhook_url = f"http://{vm_ip}:5000/webhook/receive"

col1, col2 = st.columns([3, 1])
with col1:
    st.code(webhook_url, language="text")
with col2:
    if st.button("📋 Copy", use_container_width=True):
        st.toast("URL copied!")

with st.expander("📖 API Documentation"):
    st.markdown(f"""
    ### Endpoint
    ```
    POST {webhook_url}
    ```
    
    ### Message Types
    
    **1. Simple Text Message**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "My Workflow",
      "severity": "info",
      "type": "text",
      "title": "Workflow Complete",
      "content": "Processing finished successfully"
    }}
    ```
    
    **2. Table**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "Security Scan",
      "severity": "warning",
      "type": "table",
      "title": "Vulnerability Summary",
      "content": {{
        "headers": ["Severity", "Count", "Status"],
        "rows": [
          ["Critical", "2", "Open"],
          ["High", "5", "Open"],
          ["Medium", "12", "Remediated"]
        ]
      }}
    }}
    ```
    
    **3. List**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "Deployment",
      "severity": "info",
      "type": "list",
      "title": "Deployed Services",
      "content": ["API Gateway", "Auth Service", "Database"]
    }}
    ```
    
    **4. Code Block**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "Log Alert",
      "severity": "error",
      "type": "code",
      "title": "Error Trace",
      "content": "ERROR: Connection timeout\\nStack trace..."
    }}
    ```
    
    **5. JSON Data**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "API Response",
      "severity": "info",
      "type": "json",
      "title": "Response Payload",
      "content": {{"status": 200, "data": [{{"id": 1}}]}}
    }}
    ```
    
    ### Severity Levels
    - `info` 🔵 - Informational messages
    - `warning` 🟡 - Warnings
    - `error` 🟠 - Errors
    - `critical` 🔴 - Critical alerts
    """)

st.divider()

# Filters
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    sources = ["All"] + get_sources()
    source_filter = st.selectbox("Source", sources)

with col2:
    severity_filter = st.selectbox("Severity", ["All", "Info", "Warning", "Error", "Critical"])

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Get messages
messages_df = get_webhook_messages(
    limit=100,
    severity_filter=severity_filter,
    source_filter=source_filter if source_filter != "All" else None
)

if messages_df.empty:
    st.info("No webhook messages yet. Send a test POST request to get started!")
else:
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Messages", len(messages_df))
    with col2:
        info_count = len(messages_df[messages_df['severity'] == 'info'])
        st.metric("Info", info_count)
    with col3:
        warning_count = len(messages_df[messages_df['severity'] == 'warning'])
        st.metric("Warnings", warning_count)
    with col4:
        error_count = len(messages_df[messages_df['severity'].isin(['error', 'critical'])])
        st.metric("Errors", error_count, delta_color="inverse")
    
    st.divider()
    
    # Message list
    for idx, row in messages_df.iterrows():
        severity = row['severity']
        message_type = row.get('message_type', 'text') if 'message_type' in row else 'text'
        
        # Color based on severity
        if severity == 'critical':
            border_color = "#DC2626"
            icon = "🔴"
        elif severity == 'error':
            border_color = "#EA580C"
            icon = "🟠"
        elif severity == 'warning':
            border_color = "#F59E0B"
            icon = "🟡"
        else:
            border_color = "#1A73E8"
            icon = "🔵"
        
        with st.container():
            col1, col2 = st.columns([20, 1])
            
            with col1:
                card_bg = "#2D2D2D" if is_dark else "#F8F9FA"
                
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding: 12px; margin-bottom: 12px; background: {card_bg}; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>{icon} <strong>{row['source']}</strong> · {severity.upper()} · {message_type.upper()}</span>
                        <span style="color: #9AA0A6; font-size: 0.9em;">{row['received_at']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render content
                with st.container():
                    render_message_content(row, is_dark)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            with col2:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    delete_message(row['id'])
                    st.rerun()

logger.info("Webhook dashboard loaded")

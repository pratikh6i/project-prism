"""
Webhook Dashboard
=================
View webhook messages received from automated workflows.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_setting, get_connection
from utils.logger import logger

st.set_page_config(page_title="Webhooks | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3, th, td { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
    </style>""", unsafe_allow_html=True)


def get_webhook_messages(limit=100, severity_filter=None, source_filter=None):
    """Fetch webhook messages from database."""
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
    except:
        conn.close()
        return pd.DataFrame(columns=['id', 'source', 'severity', 'message', 'payload', 'received_at'])


def get_sources():
    """Get unique sources."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source FROM webhook_messages ORDER BY source")
    sources = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sources


def delete_message(msg_id):
    """Delete a webhook message."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM webhook_messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()


st.title("📡 Webhook Dashboard")
st.markdown("View incoming webhook messages from your automated workflows")

st.divider()

# Webhook URL info
st.markdown("##### Webhook Endpoint")
vm_ip = "35.200.238.102"  # Update with your actual VM IP
webhook_url = f"http://{vm_ip}:5000/webhook/receive"

col1, col2 = st.columns([3, 1])
with col1:
    st.code(webhook_url, language="text")
with col2:
    if st.button("📋 Copy", use_container_width=True):
        st.toast("URL copied to clipboard!")

with st.expander("📖 How to use this webhook"):
    st.markdown(f"""
    **Send POST requests to:**
    ```
    {webhook_url}
    ```
    
    **Request Body (JSON):**
    ```json
    {{
      "secret": "prism-webhook-2026",
      "source": "GCP Workflow",
      "severity": "info",
      "message": "Your message here",
      "data": {{"key": "value"}}
    }}
    ```
    
    **Severity levels:** `info`, `warning`, `error`, `critical`
    
    **Example cURL:**
    ```bash
    curl -X POST {webhook_url} \\
      -H "Content-Type: application/json" \\
      -d '{{"secret":"prism-webhook-2026","source":"Test","severity":"info","message":"Hello from workflow!"}}'
    ```
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
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding: 12px; margin-bottom: 8px; background: {'#2D2D2D' if theme == 'dark' else '#F8F9FA'}; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>{icon} <strong>{row['source']}</strong> · {severity.upper()}</span>
                        <span style="color: #9AA0A6; font-size: 0.9em;">{row['received_at']}</span>
                    </div>
                    <div>{row['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    delete_message(row['id'])
                    st.rerun()

logger.info("Webhook dashboard loaded")

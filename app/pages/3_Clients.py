"""
Client Configuration
====================
Manage GCP project mappings and client settings.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_clients, add_client, delete_client, get_setting
from utils.logger import logger

st.set_page_config(page_title="Clients | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
        input, textarea, select { background-color: var(--card-bg) !important; color: var(--text) !important; }
    </style>""", unsafe_allow_html=True)

st.title("👥 Clients")
st.markdown("Manage client configurations and GCP project mappings.")

st.divider()

clients_df = get_clients()

if clients_df.empty:
    st.info("No clients yet. Add one below.")
else:
    st.markdown("##### Configured Clients")
    st.dataframe(
        clients_df[['client_name', 'gcp_project_id', 'created_at']],
        use_container_width=True,
        hide_index=True
    )
    
    with st.expander("🗑️ Delete a client"):
        client_to_delete = st.selectbox("Select client", options=clients_df['client_name'].tolist())
        
        st.warning("⚠️ This will permanently delete the client and all related data.")
        confirm = st.text_input("Type client name to confirm:", key="confirm_delete")
        
        if st.button("Delete", type="secondary"):
            if confirm == client_to_delete:
                client_id = clients_df[clients_df['client_name'] == client_to_delete]['id'].values[0]
                if delete_client(client_id):
                    st.success(f"Deleted: {client_to_delete}")
                    st.rerun()
            else:
                st.error("Name doesn't match.")

st.divider()

st.markdown("##### Add New Client")

with st.form("add_client_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name", placeholder="e.g., Acme Corp")
    
    with col2:
        gcp_project = st.text_input("GCP Project ID", placeholder="e.g., acme-prod-12345")
    
    submitted = st.form_submit_button("Add Client", type="primary")
    
    if submitted:
        if not client_name or not gcp_project:
            st.error("Both fields are required.")
        else:
            success, message = add_client(client_name, gcp_project)
            if success:
                st.success(f"Added: {client_name}")
                st.rerun()
            else:
                st.error(message)

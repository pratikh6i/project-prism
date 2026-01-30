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
from utils.db import get_clients, add_client, delete_client
from utils.logger import logger

st.set_page_config(page_title="Clients | Prism", page_icon="🔷", layout="wide")

st.title("👥 Clients")
st.markdown("Manage your client configurations and GCP project mappings.")

st.divider()

# Current Clients
clients_df = get_clients()

if clients_df.empty:
    st.info("No clients configured yet. Add one below.")
else:
    st.markdown("##### Configured Clients")
    st.dataframe(
        clients_df[['client_name', 'gcp_project_id', 'created_at']],
        use_container_width=True,
        hide_index=True
    )
    
    # Delete option
    with st.expander("Delete a client"):
        client_to_delete = st.selectbox(
            "Select client",
            options=clients_df['client_name'].tolist()
        )
        if st.button("Delete", type="secondary"):
            client_id = clients_df[clients_df['client_name'] == client_to_delete]['id'].values[0]
            if delete_client(client_id):
                st.success(f"Deleted: {client_to_delete}")
                st.rerun()

st.divider()

# Add New Client
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
                logger.info(f"Client added: {client_name}")
                st.rerun()
            else:
                st.error(message)

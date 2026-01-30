"""
Project Prism - Client Management
=================================
CRUD interface for managing client configurations.
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import init_db, add_client, get_clients, delete_client
from utils.logger import logger


# Page configuration
st.set_page_config(
    page_title="Clients | Project Prism",
    page_icon="👥",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, 'r') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database
init_db()


def render_add_client_form():
    """Render the add client form."""
    st.markdown("#### ➕ Add New Client")
    
    with st.form("add_client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input(
                "Client Name",
                placeholder="Acme Corporation",
                help="Enter the client's organization name"
            )
        
        with col2:
            project_id = st.text_input(
                "GCP Project ID",
                placeholder="acme-prod-123456",
                help="Enter the GCP Project ID (must be unique)"
            )
        
        submitted = st.form_submit_button("➕ Add Client", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not client_name or not client_name.strip():
                st.error("❌ Client name is required.")
                return
            
            if not project_id or not project_id.strip():
                st.error("❌ GCP Project ID is required.")
                return
            
            # Validate project ID format (lowercase, numbers, hyphens only)
            import re
            if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', project_id.lower()):
                st.warning("⚠️ Project ID should follow GCP naming conventions (lowercase, numbers, hyphens).")
            
            # Add the client
            success, message = add_client(client_name.strip(), project_id.strip())
            
            if success:
                st.success(f"✅ {message}")
                logger.info(f"Client added: {client_name}")
                st.rerun()
            else:
                st.error(f"❌ {message}")


def render_clients_table():
    """Render the clients table."""
    st.markdown("#### 📋 Existing Clients")
    
    clients_df = get_clients()
    
    if clients_df.empty:
        st.info("No clients found. Add your first client above! 👆")
        return
    
    # Display stats
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Total Clients:** {len(clients_df)}")
    
    with col2:
        # Refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Format the dataframe for display
    display_df = clients_df.copy()
    display_df.columns = ['ID', 'Client Name', 'GCP Project ID', 'Created At']
    
    # Format the date column
    display_df['Created At'] = pd.to_datetime(display_df['Created At']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Client Name": st.column_config.TextColumn("Client Name", width="medium"),
            "GCP Project ID": st.column_config.TextColumn("GCP Project ID", width="medium"),
            "Created At": st.column_config.TextColumn("Created At", width="medium"),
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_delete_section():
    """Render the delete client section."""
    st.markdown("#### 🗑️ Remove Client")
    
    clients_df = get_clients()
    
    if clients_df.empty:
        return
    
    # Create options for selectbox
    options = ["-- Select a client to delete --"] + [
        f"{row['client_name']} ({row['gcp_project_id']})"
        for _, row in clients_df.iterrows()
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected = st.selectbox(
            "Select Client",
            options=options,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
            if selected == "-- Select a client to delete --":
                st.warning("Please select a client first.")
            else:
                # Find the client ID
                client_name = selected.split(" (")[0]
                client_row = clients_df[clients_df['client_name'] == client_name]
                
                if not client_row.empty:
                    client_id = client_row.iloc[0]['id']
                    
                    success, message = delete_client(client_id)
                    
                    if success:
                        st.success(f"✅ {message}")
                        logger.info(f"Client deleted: {client_name}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")


def render_page():
    """Render the Clients page."""
    st.title("👥 Client Management")
    st.markdown("### Manage your client configurations and GCP projects")
    
    st.divider()
    
    # Add client form
    render_add_client_form()
    
    st.divider()
    
    # Clients table
    render_clients_table()
    
    st.divider()
    
    # Delete section
    render_delete_section()
    
    # Footer info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="
            background: #E8F0FE;
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #1A73E8;
        ">
            <p style="color: #1A73E8; font-size: 0.85rem; margin: 0;">
                💡 <strong>Tip:</strong> Client data is stored in a persistent SQLite database 
                and will survive container restarts and updates.
            </p>
        </div>
    """, unsafe_allow_html=True)


# Run the page
render_page()

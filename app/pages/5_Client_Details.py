"""
Client Details Page
===================
View and edit details for a specific client.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_client_by_id, get_client_details, save_client_detail, get_setting

st.set_page_config(page_title="Client Details | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
        input, textarea { background-color: var(--card-bg) !important; color: var(--text) !important; }
    </style>""", unsafe_allow_html=True)

# Get client ID from session
client_id = st.session_state.get('selected_client_id')

if not client_id:
    st.warning("No client selected. Go back to Dashboard and click a client card.")
    if st.button("← Back to Dashboard"):
        st.switch_page("main.py")
    st.stop()

# Get client info
client = get_client_by_id(client_id)

if not client:
    st.error("Client not found.")
    st.stop()

st.title(f"🏢 {client['client_name']}")
st.caption(f"GCP Project: `{client['gcp_project_id']}`")

st.divider()

# Get existing details
details = get_client_details(client_id)

st.markdown("##### Client Information")
st.markdown("Add notes, contacts, or any relevant data for this client.")

# Editable fields
with st.form("client_details_form"):
    
    contact_name = st.text_input(
        "Primary Contact",
        value=details.get('contact_name', ''),
        placeholder="e.g., John Smith"
    )
    
    contact_email = st.text_input(
        "Contact Email",
        value=details.get('contact_email', ''),
        placeholder="e.g., john@client.com"
    )
    
    org_id = st.text_input(
        "GCP Organization ID",
        value=details.get('org_id', ''),
        placeholder="e.g., 123456789"
    )
    
    notes = st.text_area(
        "Notes",
        value=details.get('notes', ''),
        placeholder="Any relevant notes about this client...",
        height=150
    )
    
    submitted = st.form_submit_button("Save Details", type="primary")
    
    if submitted:
        save_client_detail(client_id, 'contact_name', contact_name)
        save_client_detail(client_id, 'contact_email', contact_email)
        save_client_detail(client_id, 'org_id', org_id)
        save_client_detail(client_id, 'notes', notes)
        st.success("✅ Details saved!")

st.divider()

if st.button("← Back to Dashboard"):
    st.switch_page("main.py")

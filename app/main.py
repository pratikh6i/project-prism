"""
Dashboard - Main Entry Point
=============================
Shows clients as clickable cards with theme toggle.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.db import init_db, get_clients, get_setting, set_setting
from utils.logger import logger


def load_theme():
    """Load and apply theme from settings."""
    theme = get_setting('theme', 'light')
    
    if theme == 'dark':
        css = """
        <style>
            :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; --border: #404040; --primary: #4DA6FF; }
            html, body, [class*="css"], p, span, div, label, h1, h2, h3, h4, h5, h6, li, td, th { color: var(--text) !important; }
            .stApp { background-color: var(--bg) !important; }
            [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
            .client-card { background: var(--card-bg); border: 1px solid var(--border); }
            input, textarea, select { background-color: var(--card-bg) !important; color: var(--text) !important; }
        </style>
        """
    else:
        css = """
        <style>
            :root { --bg: #FFFFFF; --text: #202124; --card-bg: #F8F9FA; --border: #E0E0E0; --primary: #1A73E8; }
            html, body, [class*="css"], p, span, div, label, h1, h2, h3, h4, h5, h6, li, td, th { color: var(--text) !important; }
            .stApp { background-color: var(--bg) !important; }
            [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
            .client-card { background: #FFFFFF; border: 1px solid var(--border); }
        </style>
        """
    
    st.markdown(css, unsafe_allow_html=True)
    return theme


def configure_page():
    st.set_page_config(
        page_title="Dashboard | Prism",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🔷 Prism</h1>", unsafe_allow_html=True)
        st.divider()
        
        # Theme toggle
        current_theme = get_setting('theme', 'light')
        theme_label = "🌙 Dark Mode" if current_theme == 'light' else "☀️ Light Mode"
        
        if st.button(theme_label, use_container_width=True):
            new_theme = 'dark' if current_theme == 'light' else 'light'
            set_setting('theme', new_theme)
            st.rerun()
        
        st.divider()
        st.caption("v1.3 · Cloud SecOps")


def render_dashboard():
    st.title("Dashboard")
    st.markdown("Click on a client card to view details.")
    
    st.divider()
    
    clients_df = get_clients()
    
    if clients_df.empty:
        st.info("No clients yet. Go to **Clients** page to add one.")
        return
    
    # Display clients as cards in a grid
    cols = st.columns(3)
    
    for idx, row in clients_df.iterrows():
        col = cols[idx % 3]
        
        with col:
            # Card container
            card_clicked = st.button(
                f"🏢 {row['client_name']}\n\n📁 {row['gcp_project_id']}",
                key=f"client_{row['id']}",
                use_container_width=True
            )
            
            if card_clicked:
                st.session_state['selected_client_id'] = row['id']
                st.switch_page("pages/5_Client_Details.py")


def main():
    configure_page()
    init_db()
    theme = load_theme()
    render_sidebar()
    render_dashboard()
    logger.info("Dashboard loaded")


if __name__ == "__main__":
    main()

"""
Project Prism - Main Application Entry Point
=============================================
A minimalist SecOps dashboard for Cloud Security Engineers.
"""

import os
import sys
from pathlib import Path

import streamlit as st

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.db import init_db
from utils.logger import logger


def load_css():
    """Load custom CSS."""
    css_path = Path(__file__).parent / "assets" / "style.css"
    
    if css_path.exists():
        with open(css_path, 'r') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def configure_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Prism | SecOps",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_sidebar():
    """Render a clean, minimal sidebar."""
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem 0;">
                <h1 style="color: #1A73E8; margin: 0; font-size: 1.6rem;">🔷 Prism</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Simple version info
        st.caption("v1.2 · Google Cloud SecOps")


def render_home():
    """Render a minimal, clean home page."""
    st.title("Welcome to Prism")
    st.markdown("Your internal toolkit for Cloud Security Operations.")
    
    st.divider()
    
    # Simple status section
    st.markdown("##### Quick Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clients Configured", "—")  # Will update dynamically later
    with col2:
        st.metric("Environment", "Production")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Getting started - very minimal
    st.info("👈 Use the **Tools** menu in the sidebar to access SCC Export Cleaning and other utilities.")


def main():
    """Main application entry point."""
    configure_page()
    load_css()
    init_db()
    render_sidebar()
    render_home()
    logger.info("App loaded")


if __name__ == "__main__":
    main()

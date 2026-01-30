"""
Project Prism - Main Application Entry Point
=============================================
A SecOps tool built for Google Cloud Partners.
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
    """Load custom CSS for Google Cloud Partner aesthetic."""
    css_path = Path(__file__).parent / "assets" / "style.css"
    
    if css_path.exists():
        with open(css_path, 'r') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        logger.debug("Custom CSS loaded successfully")
    else:
        logger.warning(f"CSS file not found at {css_path}")


def configure_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Project Prism | SecOps Tool",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/pratikh6i/project-prism',
            'Report a bug': 'https://github.com/pratikh6i/project-prism/issues',
            'About': """
                ## Project Prism 🔷
                
                A Security Operations tool built for Google Cloud Partners.
                
                **Features:**
                - SCC Export Cleaning (Refractor)
                - Client Management
                - Ops Wiki (SOPs)
                
                Built with ❤️ using Streamlit
            """
        }
    )


def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="color: #1A73E8; margin: 0;">🔷 Prism</h1>
                <p style="color: #5F6368; font-size: 0.875rem; margin-top: 0.5rem;">
                    SecOps Toolkit
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Info section
        st.markdown("""
            <div style="padding: 0.5rem; background: #E8F0FE; border-radius: 8px; margin-bottom: 1rem;">
                <p style="color: #1A73E8; font-size: 0.75rem; margin: 0;">
                    <strong>Google Cloud Partner</strong><br>
                    Security Operations Center
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Spacer to push version to bottom
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        
        # Version info at bottom
        st.markdown("""
            <div style="position: fixed; bottom: 1rem; left: 1rem;">
                <p style="color: #9AA0A6; font-size: 0.75rem;">
                    v1.0.0 | © 2024
                </p>
            </div>
        """, unsafe_allow_html=True)


def render_home():
    """Render the home page content."""
    st.title("🔷 Project Prism")
    st.markdown("### Your Security Operations Command Center")
    
    st.divider()
    
    # Quick stats row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #1A73E8;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            ">
                <h3 style="color: #1A73E8; margin: 0;">🔄 Refractor</h3>
                <p style="color: #5F6368; margin-top: 0.5rem;">
                    Clean and process SCC exports into organized Excel reports.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #34A853;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            ">
                <h3 style="color: #34A853; margin: 0;">👥 Clients</h3>
                <p style="color: #5F6368; margin-top: 0.5rem;">
                    Manage your client configurations and GCP projects.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #FBBC04;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            ">
                <h3 style="color: #FBBC04; margin: 0;">📚 Ops Wiki</h3>
                <p style="color: #5F6368; margin-top: 0.5rem;">
                    Standard Operating Procedures and documentation.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("### 🚀 Getting Started")
    
    st.markdown("""
        Use the **sidebar navigation** to access different tools:
        
        1. **Refractor** - Upload SCC exports and generate clean, categorized Excel reports
        2. **Clients** - Add, view, and manage your client configurations
        3. **Ops Wiki** - Access standard operating procedures and runbooks
        
        ---
        
        💡 **Tip:** All data is persisted locally, so your configurations will survive 
        container restarts and updates.
    """)


def main():
    """Main application entry point."""
    # Configure page first (must be first Streamlit command)
    configure_page()
    
    # Load custom styling
    load_css()
    
    # Initialize database
    init_db()
    
    # Render sidebar
    render_sidebar()
    
    # Render home page content
    render_home()
    
    logger.info("Application loaded successfully")


if __name__ == "__main__":
    main()

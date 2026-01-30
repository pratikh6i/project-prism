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
        # Logo and title with higher contrast
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <h1 style="color: #1A73E8; margin: 0; font-size: 1.8rem; font-weight: 700;">🔷 Prism</h1>
                <p style="color: #3C4043; font-size: 0.9rem; font-weight: 500; margin-top: 0.2rem;">
                    SecOps Toolkit
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Info section with custom banner class
        st.markdown("""
            <div class="custom-banner">
                <p style="margin: 0; font-size: 0.8rem;">
                    <strong>Google Cloud Partner</strong><br>
                    Security Operations Center
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # NAVIGATION HELP for users (since it might be collapsed)
        st.info("👈 Use the menu above to switch between tools.")
        
        # Spacer to push version to bottom
        st.markdown("<br>" * 3, unsafe_allow_html=True)
        
        # Version info at bottom
        st.markdown("""
            <div style="padding: 1rem; border-top: 1px solid #DADCE0; margin-top: 2rem;">
                <p style="color: #5F6368; font-size: 0.75rem; margin: 0;">
                    v1.1.0 | Google Cloud SecOps
                </p>
            </div>
        """, unsafe_allow_html=True)


def render_home():
    """Render the home page content."""
    st.title("🔷 Project Prism")
    st.markdown("##### Your Security Operations Command Center")
    
    st.divider()
    
    # Quick access row with improved card design
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #DADCE0;
                border-top: 4px solid #1A73E8;
                height: 180px;
            ">
                <h3 style="color: #1A73E8; margin: 0;">🔄 Refractor</h3>
                <p style="color: #3C4043; margin-top: 0.8rem; font-size: 0.95rem;">
                    Automated SCC Export Cleaning. Convert JSON/CSV finding exports into organized audit reports.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #DADCE0;
                border-top: 4px solid #34A853;
                height: 180px;
            ">
                <h3 style="color: #34A853; margin: 0;">👥 Clients</h3>
                <p style="color: #3C4043; margin-top: 0.8rem; font-size: 0.95rem;">
                    Centralized management for client configurations, project IDs, and persistent settings.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #DADCE0;
                border-top: 4px solid #FBBC04;
                height: 180px;
            ">
                <h3 style="color: #FBBC04; margin: 0;">📚 Ops Wiki</h3>
                <p style="color: #3C4043; margin-top: 0.8rem; font-size: 0.95rem;">
                    Standard Operating Procedures (SOPs), runbooks, and security best practices repository.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Deployment status indicator (Simulated)
    st.success("✅ **Deployment Sync:** Your environment is successfully pulling from the latest Git main branch.")
    
    # Getting started section
    st.markdown("### 🚀 Getting Started")
    
    left, right = st.columns([2, 1])
    with left:
        st.markdown("""
            1. **Select a tool** from the sidebar on the left.
            2. **Manage Clients** first to ensure all project IDs are correctly mapped.
            3. **Run Refractor** to process security findings for your specific clients.
            
            All data you input in the Clients page is stored in `prism.db` on your VM, ensuring it remains intact even if you restart this service.
        """)
    
    with right:
        st.info("""
            **Service Info:**
            - **Environment:** Production
            - **Stack:** Streamlit / Docker / SQLite
            - **Sync:** GitOps Enabled
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

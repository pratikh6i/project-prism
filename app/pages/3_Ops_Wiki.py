"""
Project Prism - Ops Wiki
========================
Standard Operating Procedures and documentation.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


# Page configuration
st.set_page_config(
    page_title="Ops Wiki | Project Prism",
    page_icon="📚",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, 'r') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page():
    """Render the Ops Wiki page."""
    st.title("📚 Ops Wiki")
    st.markdown("### Standard Operating Procedures & Documentation")
    
    st.divider()
    
    # Coming soon banner
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1A73E8 0%, #34A853 100%);
            padding: 3rem;
            border-radius: 16px;
            text-align: center;
            margin: 2rem 0;
        ">
            <h2 style="color: white; margin: 0;">🚧 Coming Soon</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 1rem;">
                The Ops Wiki is under construction. Check back soon for SOPs and runbooks!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Planned features
    st.markdown("#### 📋 Planned Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #1A73E8;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                margin-bottom: 1rem;
            ">
                <h4 style="color: #1A73E8; margin: 0;">📝 SOPs</h4>
                <p style="color: #5F6368; margin-top: 0.5rem; margin-bottom: 0;">
                    Step-by-step standard operating procedures for common SecOps tasks.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #EA4335;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            ">
                <h4 style="color: #EA4335; margin: 0;">🚨 Incident Response</h4>
                <p style="color: #5F6368; margin-top: 0.5rem; margin-bottom: 0;">
                    Playbooks and checklists for security incident handling.
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
                margin-bottom: 1rem;
            ">
                <h4 style="color: #34A853; margin: 0;">🔍 Runbooks</h4>
                <p style="color: #5F6368; margin-top: 0.5rem; margin-bottom: 0;">
                    Detailed runbooks for GCP security tools and services.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #FBBC04;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            ">
                <h4 style="color: #FBBC04; margin: 0;">📈 Best Practices</h4>
                <p style="color: #5F6368; margin-top: 0.5rem; margin-bottom: 0;">
                    Security best practices and compliance guidelines.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick links section
    st.markdown("#### 🔗 Quick Links")
    
    st.markdown("""
        <div style="
            background: #F8F9FA;
            padding: 1.5rem;
            border-radius: 8px;
        ">
            <p style="margin: 0.5rem 0;">
                🔹 <a href="https://cloud.google.com/security-command-center/docs" target="_blank">
                    Security Command Center Documentation
                </a>
            </p>
            <p style="margin: 0.5rem 0;">
                🔹 <a href="https://cloud.google.com/security/best-practices" target="_blank">
                    GCP Security Best Practices
                </a>
            </p>
            <p style="margin: 0.5rem 0;">
                🔹 <a href="https://cloud.google.com/iam/docs" target="_blank">
                    IAM Documentation
                </a>
            </p>
            <p style="margin: 0.5rem 0;">
                🔹 <a href="https://cloud.google.com/logging/docs" target="_blank">
                    Cloud Logging Documentation
                </a>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    logger.debug("Ops Wiki page loaded")


# Run the page
render_page()

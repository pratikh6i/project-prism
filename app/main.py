"""
Prism - Simple SecOps Dashboard
================================
SCC Cleaner + Ops Wiki + Webhook Dashboard
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.db import init_db, get_setting, set_setting
from utils.logger import logger

st.set_page_config(
    page_title="Prism | SecOps Tools",
    page_icon="🔷",
    layout="wide",
)

# Initialize database
init_db()

# Theme toggle in sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🔷 Prism</h1>", unsafe_allow_html=True)
    st.divider()
    
    current_theme = get_setting('theme', 'light')
    theme_label = "🌙 Dark Mode" if current_theme == 'light' else "☀️ Light Mode"
    
    if st.button(theme_label, use_container_width=True):
        new_theme = 'dark' if current_theme == 'light' else 'light'
        set_setting('theme', new_theme)
        st.rerun()
    
    st.divider()
    st.caption("v2.0 · Cloud SecOps")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
    </style>""", unsafe_allow_html=True)

# Main page
st.title("Prism")
st.markdown("SecOps tools for Cloud Security Engineers")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔄 SCC Export Cleaner")
    st.markdown("Clean SCC finding exports")
    if st.button("Open SCC Cleaner", use_container_width=True, type="primary"):
        st.switch_page("pages/1_SCC_Cleaner.py")

with col2:
    st.markdown("### 📚 Ops Wiki")
    st.markdown("Embedded runbooks & SOPs")
    if st.button("Open Ops Wiki", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Ops_Wiki.py")

with col3:
    st.markdown("### 📡 Webhook Dashboard")
    st.markdown("View workflow notifications")
    if st.button("Open Webhooks", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Webhook_Dashboard.py")

logger.info("Prism loaded")

"""
Tools Page
==========
Central hub for SecOps utilities.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_setting

st.set_page_config(page_title="Tools | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
    </style>""", unsafe_allow_html=True)

st.title("🛠️ Tools")
st.markdown("Select a tool to get started.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔄 SCC Export Cleaner")
    st.markdown("Clean SCC finding exports into organized Excel reports.")
    if st.button("Open SCC Cleaner", key="refractor", use_container_width=True):
        st.switch_page("pages/2_Refractor.py")

with col2:
    st.markdown("### 📚 Ops Wiki")
    st.markdown("Access embedded runbooks and SOPs.")
    if st.button("Open Ops Wiki", key="wiki", use_container_width=True):
        st.switch_page("pages/4_Ops_Wiki.py")

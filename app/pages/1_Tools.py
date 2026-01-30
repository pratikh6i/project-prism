"""
Tools Page
==========
Central hub for all SecOps utilities.
"""

import streamlit as st

st.set_page_config(page_title="Tools | Prism", page_icon="🔷", layout="wide")

st.title("🛠️ Tools")
st.markdown("Select a tool below to get started.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        ### 🔄 SCC Export Cleaner
        Clean and organize Security Command Center finding exports into Excel reports.
        
        **Use when:** You have a raw CSV/JSON export from SCC and need a categorized audit report.
    """)
    if st.button("Open SCC Cleaner", key="refractor"):
        st.switch_page("pages/2_Refractor.py")

with col2:
    st.markdown("""
        ### 📚 Ops Wiki
        Access standard operating procedures and runbooks for common security tasks.
        
        **Use when:** You need step-by-step guidance on handling findings or incidents.
    """)
    if st.button("Open Ops Wiki", key="wiki"):
        st.switch_page("pages/4_Ops_Wiki.py")

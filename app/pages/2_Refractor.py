"""
SCC Export Cleaner (Refractor)
==============================
Clean SCC finding exports into organized Excel reports.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processor import process_scc_export, validate_file
from utils.logger import logger
from utils.db import get_setting

st.set_page_config(page_title="SCC Cleaner | Prism", page_icon="🔷", layout="wide")

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

st.title("🔄 SCC Export Cleaner")
st.markdown("Upload a raw SCC finding export (CSV) and get an organized Excel report.")

st.divider()

uploaded_file = st.file_uploader("Drop your SCC export here", type=['csv'])

if uploaded_file:
    is_valid, message = validate_file(uploaded_file)
    
    if not is_valid:
        st.error(f"❌ {message}")
    else:
        st.success("✅ File validated.")
        
        with st.expander("Preview raw data"):
            df = pd.read_csv(uploaded_file)
            uploaded_file.seek(0)
            st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("Generate Report", type="primary"):
            with st.spinner("Processing..."):
                try:
                    output = process_scc_export(uploaded_file)
                    st.success("✅ Report ready!")
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=output,
                        file_name="scc_findings_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
else:
    st.info("👆 Upload an SCC export to begin.")

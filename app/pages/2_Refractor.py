"""
SCC Export Cleaner
==================
Upload raw SCC CSV export → get cleaned Excel with only relevant columns.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processor import validate_file, process_scc_export, get_project_summary
from utils.logger import logger
from utils.db import get_setting

st.set_page_config(page_title="SCC Cleaner | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3, th, td { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
    </style>""", unsafe_allow_html=True)

st.title("🔄 SCC Export Cleaner")
st.markdown("Upload a raw SCC finding export (CSV) → Get a clean Excel with only relevant columns.")

st.divider()

# File Upload
uploaded_file = st.file_uploader(
    "Drop your SCC CSV export here",
    type=['csv'],
    help="Export findings from Security Command Center as CSV"
)

if uploaded_file:
    # Validate
    is_valid, message = validate_file(uploaded_file)
    
    if not is_valid:
        st.error(f"❌ {message}")
    else:
        st.success(f"✅ {message}")
        
        # Show project summary
        st.markdown("##### 📊 Project Summary")
        try:
            summary_df = get_project_summary(uploaded_file)
            if not summary_df.empty:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                with col2:
                    st.metric("Total Projects", len(summary_df))
                    st.metric("Total Findings", summary_df['Finding Count'].sum())
        except Exception as e:
            st.warning(f"Could not generate summary: {e}")
        
        st.divider()
        
        # Process button
        if st.button("🚀 Clean & Generate Excel", type="primary", use_container_width=True):
            with st.spinner("Processing... This may take a moment for large files."):
                try:
                    output, stats = process_scc_export(uploaded_file)
                    
                    st.success("✅ Processing complete!")
                    
                    # Show stats
                    st.markdown("##### 📈 Processing Stats")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original Columns", stats['original_columns'])
                    with col2:
                        st.metric("Cleaned Columns", stats['cleaned_columns'])
                    with col3:
                        st.metric("Rows Processed", stats['original_rows'])
                    
                    if stats['missing_columns'] > 0:
                        with st.expander(f"ℹ️ {stats['missing_columns']} reference columns not found in CSV"):
                            st.caption("These columns were in the reference list but not in your export. This is normal - not all exports have all columns.")
                    
                    st.divider()
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Cleaned Excel",
                        data=output,
                        file_name="scc_findings_cleaned.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    logger.info(f"SCC export processed: {stats['original_rows']} rows, {stats['cleaned_columns']} columns")
                    
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    logger.error(f"SCC processing error: {e}")

else:
    # Instructions when no file uploaded
    st.info("👆 Upload an SCC CSV export to begin.")
    
    with st.expander("ℹ️ How to export from SCC"):
        st.markdown("""
        1. Go to **Security Command Center** in GCP Console
        2. Navigate to **Findings**
        3. Apply your filters (project, severity, etc.)
        4. Click **Export** → **CSV**
        5. Upload the downloaded file here
        """)
    
    with st.expander("📋 Columns that will be kept"):
        st.markdown("""
        The cleaner keeps only the essential columns for security analysis:
        - **Project info**: Project name, resource display name, type
        - **Finding details**: State, category, severity, class
        - **Timing**: Event time, create time
        - **Vulnerability data**: CVE ID, CVSS score, fix availability
        - **Context**: Description, next steps, compliances
        - **Attack exposure**: Score, state, result
        
        All other columns are removed to reduce noise.
        """)

"""
SCC Export Cleaner (Refractor)
==============================
Clean and organize Security Command Center exports into readable Excel reports.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_processor import process_scc_export, validate_file
from utils.logger import logger

st.set_page_config(page_title="SCC Cleaner | Prism", page_icon="🔷", layout="wide")

st.title("🔄 SCC Export Cleaner")
st.markdown("Upload a raw SCC finding export (CSV) and get an organized Excel report.")

st.divider()

# File Upload
uploaded_file = st.file_uploader(
    "Drop your SCC export here",
    type=['csv'],
    help="Accepts CSV exports from Security Command Center"
)

if uploaded_file:
    # Validate
    is_valid, message = validate_file(uploaded_file)
    
    if not is_valid:
        st.error(f"❌ {message}")
    else:
        st.success("✅ File validated. Ready to process.")
        
        # Preview
        with st.expander("Preview raw data"):
            df = pd.read_csv(uploaded_file)
            uploaded_file.seek(0)  # Reset for processing
            st.dataframe(df.head(10), use_container_width=True)
        
        # Process
        if st.button("Generate Report", type="primary"):
            with st.spinner("Processing findings..."):
                try:
                    output = process_scc_export(uploaded_file)
                    
                    st.success("✅ Report generated!")
                    
                    # Download
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=output,
                        file_name="scc_findings_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    logger.info("SCC report generated successfully")
                    
                except Exception as e:
                    st.error(f"Processing failed: {str(e)}")
                    logger.error(f"SCC processing error: {e}")
else:
    st.info("👆 Upload an SCC export to begin.")

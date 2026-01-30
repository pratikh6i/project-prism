"""
Project Prism - Refractor (SCC Cleaning Tool)
=============================================
Clean and process Security Command Center exports.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processor import process_scc_export, validate_scc_file
from utils.logger import logger


# Page configuration
st.set_page_config(
    page_title="Refractor | Project Prism",
    page_icon="🔄",
    layout="wide"
)

# Load custom CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path, 'r') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page():
    """Render the Refractor page."""
    st.title("🔄 Refractor")
    st.markdown("### SCC Export Cleaning Tool")
    
    st.markdown("""
        Transform raw Security Command Center exports into clean, organized Excel reports.
        The tool will:
        - Normalize column names
        - Group findings by category
        - Generate a multi-tab Excel file with summary
    """)
    
    st.divider()
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📤 Upload SCC Export")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your raw SCC export file"
        )
        
        if uploaded_file:
            try:
                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Validate the file
                is_valid, validation_msg = validate_scc_file(df)
                
                if is_valid:
                    if "Warning" in validation_msg:
                        st.warning(validation_msg)
                    else:
                        st.success(validation_msg)
                    
                    # Store in session state
                    st.session_state['scc_data'] = df
                    st.session_state['original_filename'] = uploaded_file.name
                    
                    logger.info(f"File uploaded: {uploaded_file.name} with {len(df)} rows")
                else:
                    st.error(validation_msg)
                    logger.warning(f"Invalid file uploaded: {validation_msg}")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                logger.error(f"File read error: {str(e)}")
    
    with col2:
        st.markdown("#### 📋 Upload Rules (Optional)")
        
        rules_file = st.file_uploader(
            "Choose a rules file",
            type=['csv', 'xlsx'],
            help="Optional: Upload column filtering rules",
            key="rules_uploader"
        )
        
        if rules_file:
            try:
                if rules_file.name.endswith('.csv'):
                    rules_df = pd.read_csv(rules_file)
                else:
                    rules_df = pd.read_excel(rules_file)
                
                st.session_state['rules_data'] = rules_df
                st.success(f"Rules loaded: {len(rules_df)} rules")
                logger.info(f"Rules file uploaded: {rules_file.name}")
            except Exception as e:
                st.error(f"Error reading rules: {str(e)}")
        
        st.markdown("""
            <div style="
                background: #FEF7E0;
                padding: 1rem;
                border-radius: 8px;
                border-left: 3px solid #FBBC04;
                margin-top: 1rem;
            ">
                <p style="color: #5F6368; font-size: 0.8rem; margin: 0;">
                    <strong>Rules Format:</strong><br>
                    CSV with columns:<br>
                    • category<br>
                    • columns_to_keep
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Preview and process section
    if 'scc_data' in st.session_state and st.session_state['scc_data'] is not None:
        df = st.session_state['scc_data']
        
        st.markdown("#### 👀 Data Preview")
        
        # Stats
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Rows", f"{len(df):,}")
        with stat_col2:
            st.metric("Total Columns", len(df.columns))
        with stat_col3:
            # Estimate categories
            category_cols = [col for col in df.columns if 'category' in col.lower() or 'type' in col.lower()]
            if category_cols:
                num_categories = df[category_cols[0]].nunique()
            else:
                num_categories = 1
            st.metric("Categories", num_categories)
        
        # Show preview
        with st.expander("📊 View Raw Data", expanded=False):
            st.dataframe(df.head(100), use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Process button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 Process & Generate Report", use_container_width=True, type="primary"):
                with st.spinner("Processing SCC export..."):
                    try:
                        # Get rules if available
                        rules_df = st.session_state.get('rules_data', None)
                        
                        # Process the data
                        output = process_scc_export(df, rules_df)
                        
                        # Generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        original_name = st.session_state.get('original_filename', 'export')
                        original_name = original_name.rsplit('.', 1)[0]  # Remove extension
                        output_filename = f"{original_name}_cleaned_{timestamp}.xlsx"
                        
                        st.session_state['processed_output'] = output
                        st.session_state['output_filename'] = output_filename
                        
                        st.success("✅ Processing complete!")
                        logger.info(f"SCC export processed successfully: {output_filename}")
                    
                    except Exception as e:
                        st.error(f"Processing error: {str(e)}")
                        logger.error(f"Processing error: {str(e)}")
        
        # Download section
        if 'processed_output' in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.download_button(
                    label="⬇️ Download Cleaned Report",
                    data=st.session_state['processed_output'],
                    file_name=st.session_state['output_filename'],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Clear data button
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            for key in ['scc_data', 'rules_data', 'processed_output', 'output_filename', 'original_filename']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# Run the page
render_page()

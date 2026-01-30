"""
Ops Wiki
========
Manage embedded Google Docs/Sheets for security runbooks and SOPs.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_documents, add_document, delete_document, get_setting

st.set_page_config(page_title="Ops Wiki | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
        input, textarea, select { background-color: var(--card-bg) !important; color: var(--text) !important; }
    </style>""", unsafe_allow_html=True)

st.title("📚 Ops Wiki")
st.markdown("Embedded Google Docs, Sheets, and runbooks for your team.")

st.divider()

# Get existing documents
docs_df = get_documents()

# Add new document section
with st.expander("➕ Add New Document", expanded=False):
    with st.form("add_doc_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            doc_title = st.text_input("Document Title", placeholder="e.g., Incident Response Playbook")
        
        with col2:
            doc_type = st.selectbox("Type", ["Google Doc", "Google Sheet", "Other"])
        
        doc_url = st.text_input(
            "Document URL",
            placeholder="https://docs.google.com/document/d/..."
        )
        
        st.caption("💡 Make sure the document is set to 'Anyone with link can view'")
        
        submitted = st.form_submit_button("Add Document", type="primary")
        
        if submitted:
            if not doc_title or not doc_url:
                st.error("Title and URL are required.")
            else:
                type_map = {"Google Doc": "google_doc", "Google Sheet": "google_sheet", "Other": "other"}
                if add_document(doc_title, doc_url, type_map.get(doc_type, 'other')):
                    st.success(f"Added: {doc_title}")
                    st.rerun()
                else:
                    st.error("Failed to add document.")

st.divider()

# Display documents
if docs_df.empty:
    st.info("No documents added yet. Add one above to get started.")
else:
    for idx, row in docs_df.iterrows():
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Document header
                icon = "📄" if row['doc_type'] == 'google_doc' else "📊" if row['doc_type'] == 'google_sheet' else "📎"
                st.markdown(f"### {icon} {row['title']}")
            
            with col2:
                # Delete with confirmation (requires typing title)
                with st.popover("🗑️ Delete"):
                    st.warning(f"**Delete '{row['title']}'?**")
                    st.caption("To confirm, type the document title exactly:")
                    confirm_text = st.text_input("Confirm title", key=f"confirm_{row['id']}", label_visibility="collapsed")
                    
                    if st.button("Delete Permanently", key=f"del_{row['id']}", type="secondary"):
                        if confirm_text == row['title']:
                            if delete_document(row['id']):
                                st.success("Deleted!")
                                st.rerun()
                        else:
                            st.error("Title doesn't match.")
            
            # Embed the document
            embed_url = row['doc_url']
            
            # Convert sharing links to embed links
            if 'docs.google.com/document' in embed_url:
                if '/edit' in embed_url:
                    embed_url = embed_url.replace('/edit', '/preview')
                elif '/view' in embed_url:
                    embed_url = embed_url.replace('/view', '/preview')
                elif not embed_url.endswith('/preview'):
                    embed_url = embed_url.rstrip('/') + '/preview'
            
            elif 'docs.google.com/spreadsheets' in embed_url:
                if '/edit' in embed_url:
                    embed_url = embed_url.split('/edit')[0] + '/preview'
                elif not '/preview' in embed_url:
                    embed_url = embed_url.rstrip('/') + '/preview'
            
            # Iframe for embedded view
            st.markdown(
                f'<iframe src="{embed_url}" width="100%" height="600" frameborder="0"></iframe>',
                unsafe_allow_html=True
            )
            
            # Direct link option
            st.caption(f"[Open in new tab ↗]({row['doc_url']})")
            
            st.divider()

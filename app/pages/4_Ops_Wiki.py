"""
Ops Wiki
========
Google Drive-style document list with embedded previews.
"""

import streamlit as st
import re
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_documents, add_document, delete_document, get_setting

st.set_page_config(page_title="Ops Wiki | Prism", page_icon="🔷", layout="wide")

# Apply theme
theme = get_setting('theme', 'light')
if theme == 'dark':
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; --border: #404040; --hover: #383838; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
        input { background-color: var(--card-bg) !important; color: var(--text) !important; }
        .doc-row { background: var(--card-bg); border-bottom: 1px solid var(--border); }
        .doc-row:hover { background: var(--hover); }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
        .doc-row { background: #FFFFFF; border-bottom: 1px solid #E0E0E0; }
        .doc-row:hover { background: #F5F5F5; }
    </style>""", unsafe_allow_html=True)


def extract_doc_info(url: str) -> tuple[str, str]:
    """Extract document title/type from Google URL."""
    doc_type = "other"
    title = "Untitled Document"
    
    if 'docs.google.com/document' in url:
        doc_type = "google_doc"
        title = "Google Doc"
    elif 'docs.google.com/spreadsheets' in url:
        doc_type = "google_sheet"
        title = "Google Sheet"
    elif 'docs.google.com/presentation' in url:
        doc_type = "google_slides"
        title = "Google Slides"
    elif 'drive.google.com' in url:
        doc_type = "google_drive"
        title = "Google Drive File"
    
    # Try to extract doc ID for reference
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        doc_id = match.group(1)[:8]
        title = f"{title} ({doc_id}...)"
    
    return title, doc_type


def get_icon(doc_type: str) -> str:
    icons = {
        "google_doc": "📄",
        "google_sheet": "📊",
        "google_slides": "📽️",
        "google_drive": "📁",
        "other": "📎"
    }
    return icons.get(doc_type, "📎")


st.title("📚 Ops Wiki")

# Quick add - just paste the link
st.markdown("##### Add Document")
col1, col2 = st.columns([4, 1])

with col1:
    new_url = st.text_input(
        "Paste Google Doc/Sheet link",
        placeholder="https://docs.google.com/document/d/...",
        label_visibility="collapsed"
    )

with col2:
    if st.button("Add", type="primary", use_container_width=True):
        if new_url:
            title, doc_type = extract_doc_info(new_url)
            if add_document(title, new_url, doc_type):
                st.success("Added!")
                st.rerun()
            else:
                st.error("Failed to add.")
        else:
            st.warning("Paste a link first.")

st.divider()

# Document list (Google Drive style)
docs_df = get_documents()

if docs_df.empty:
    st.info("No documents yet. Paste a Google Doc or Sheet link above.")
else:
    # Header row
    header_cols = st.columns([0.5, 4, 2, 1])
    with header_cols[0]:
        st.caption("")
    with header_cols[1]:
        st.caption("**Name**")
    with header_cols[2]:
        st.caption("**Date added**")
    with header_cols[3]:
        st.caption("")
    
    # Document rows
    for idx, row in docs_df.iterrows():
        cols = st.columns([0.5, 4, 2, 1])
        
        with cols[0]:
            st.markdown(get_icon(row['doc_type']))
        
        with cols[1]:
            # Editable title
            if st.button(row['title'], key=f"open_{row['id']}", use_container_width=True):
                st.session_state['view_doc_id'] = row['id']
                st.session_state['view_doc_url'] = row['doc_url']
                st.session_state['view_doc_title'] = row['title']
        
        with cols[2]:
            created_at = row['created_at']
            if isinstance(created_at, str):
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    st.caption(dt.strftime("%b %d, %Y"))
                except:
                    st.caption(created_at[:10] if len(created_at) > 10 else created_at)
            else:
                st.caption("—")
        
        with cols[3]:
            # Delete with popover
            with st.popover("⋮"):
                st.caption(f"**{row['title']}**")
                st.markdown(f"[Open in new tab ↗]({row['doc_url']})")
                st.divider()
                
                confirm = st.checkbox("I want to delete this", key=f"conf_{row['id']}")
                if confirm:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}", type="secondary"):
                        delete_document(row['id'])
                        st.rerun()

# Document preview (if selected)
if 'view_doc_id' in st.session_state:
    st.divider()
    st.markdown(f"### {st.session_state.get('view_doc_title', 'Preview')}")
    
    url = st.session_state['view_doc_url']
    
    # Convert to embed URL
    if 'docs.google.com/document' in url:
        if '/edit' in url:
            url = url.replace('/edit', '/preview')
        elif not '/preview' in url:
            url = url.rstrip('/') + '/preview'
    elif 'docs.google.com/spreadsheets' in url:
        if '/edit' in url:
            url = url.split('/edit')[0] + '/preview'
    
    st.markdown(
        f'<iframe src="{url}" width="100%" height="700" frameborder="0" style="border-radius: 8px;"></iframe>',
        unsafe_allow_html=True
    )
    
    if st.button("Close Preview"):
        del st.session_state['view_doc_id']
        del st.session_state['view_doc_url']
        del st.session_state['view_doc_title']
        st.rerun()

"""
Ops Wiki
========
Google Drive-style document gallery with auto-detected file types.
Documents open in new tab.
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
is_dark = theme == 'dark'

if is_dark:
    st.markdown("""<style>
        :root { --bg: #1E1E1E; --text: #E0E0E0; --card-bg: #2D2D2D; --border: #404040; --hover: #383838; }
        html, body, [class*="css"], p, span, div, label, h1, h2, h3 { color: var(--text) !important; }
        .stApp { background-color: var(--bg) !important; }
        [data-testid="stSidebar"] { background-color: var(--card-bg) !important; }
        input { background-color: var(--card-bg) !important; color: var(--text) !important; }
        .doc-card { background: var(--card-bg); border: 1px solid var(--border); }
        .doc-card:hover { background: var(--hover); border-color: #4DA6FF; }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
        .doc-card { background: #FFFFFF; border: 1px solid #E0E0E0; }
        .doc-card:hover { background: #F5F5F5; border-color: #1A73E8; }
    </style>""", unsafe_allow_html=True)

# SVG icons for each file type
ICONS = {
    "google_doc": '''<svg viewBox="0 0 48 48" width="32" height="32"><path fill="#2196F3" d="M37,45H11c-1.7,0-3-1.3-3-3V6c0-1.7,1.3-3,3-3h19l10,10v29C40,43.7,38.7,45,37,45z"/><path fill="#BBDEFB" d="M40,16H30V6L40,16z"/><path fill="#E3F2FD" d="M30,6v10h10L30,6z"/><path fill="#1565C0" d="M30,13l2-2h6L30,3V13z"/><path fill="#E3F2FD" d="M15,23h18v2H15V23z M15,27h18v2H15V27z M15,31h18v2H15V31z M15,35h12v2H15V35z"/></svg>''',
    "google_sheet": '''<svg viewBox="0 0 48 48" width="32" height="32"><path fill="#43A047" d="M37,45H11c-1.7,0-3-1.3-3-3V6c0-1.7,1.3-3,3-3h19l10,10v29C40,43.7,38.7,45,37,45z"/><path fill="#C8E6C9" d="M40,16H30V6L40,16z"/><path fill="#E8F5E9" d="M30,6v10h10L30,6z"/><path fill="#2E7D32" d="M30,13l2-2h6L30,3V13z"/><path fill="#E8F5E9" d="M31,23H17v12h14V23z M19,33v-2h4v2H19z M19,29v-2h4v2H19z M19,25v-2h4v2H19z M25,33v-2h4v2H25z M25,29v-2h4v2H25z M25,25v-2h4v2H25z"/></svg>''',
    "google_slides": '''<svg viewBox="0 0 48 48" width="32" height="32"><path fill="#FFA000" d="M37,45H11c-1.7,0-3-1.3-3-3V6c0-1.7,1.3-3,3-3h19l10,10v29C40,43.7,38.7,45,37,45z"/><path fill="#FFECB3" d="M40,16H30V6L40,16z"/><path fill="#FFF8E1" d="M30,6v10h10L30,6z"/><path fill="#FF8F00" d="M30,13l2-2h6L30,3V13z"/><rect x="17" y="23" fill="#FFF8E1" width="14" height="10"/><rect x="17" y="23" fill="none" stroke="#FF8F00" stroke-width="1" width="14" height="10"/></svg>''',
    "google_drive": '''<svg viewBox="0 0 48 48" width="32" height="32"><path fill="#FFC107" d="M17,31l5,9H6l5-9H17z"/><path fill="#1976D2" d="M28,40H12l5-9h16L28,40z"/><path fill="#4CAF50" d="M38,31l-5-9H17l5,9H38z"/><path fill="#4CAF50" d="M22,22l-5,9l10-9H22z"/><path fill="#1976D2" d="M33,22L22,22l5,9L33,22z"/><path fill="#E64A19" d="M17,12l-5,9l10,1L17,12z"/><path fill="#E64A19" d="M33,22l-10-1l-6-9H33z"/></svg>''',
    "other": '''<svg viewBox="0 0 48 48" width="32" height="32"><path fill="#90A4AE" d="M37,45H11c-1.7,0-3-1.3-3-3V6c0-1.7,1.3-3,3-3h19l10,10v29C40,43.7,38.7,45,37,45z"/><path fill="#CFD8DC" d="M40,16H30V6L40,16z"/><path fill="#ECEFF1" d="M30,6v10h10L30,6z"/></svg>'''
}


def detect_doc_type(url: str) -> str:
    """Auto-detect document type from URL."""
    url_lower = url.lower()
    if 'docs.google.com/document' in url_lower:
        return 'google_doc'
    elif 'docs.google.com/spreadsheets' in url_lower:
        return 'google_sheet'
    elif 'docs.google.com/presentation' in url_lower:
        return 'google_slides'
    elif 'drive.google.com' in url_lower:
        return 'google_drive'
    return 'other'


def extract_title_from_url(url: str, doc_type: str) -> str:
    """Generate a readable title from URL."""
    type_names = {
        'google_doc': 'Google Doc',
        'google_sheet': 'Google Sheet',
        'google_slides': 'Google Slides',
        'google_drive': 'Drive File',
        'other': 'Document'
    }
    
    # Try to extract doc ID
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        doc_id = match.group(1)[:10]
        return f"{type_names.get(doc_type, 'Document')} ({doc_id}...)"
    
    return type_names.get(doc_type, 'Document')


st.title("📚 Ops Wiki")

# Quick add - just paste the link
col1, col2 = st.columns([5, 1])

with col1:
    new_url = st.text_input(
        "Add document",
        placeholder="Paste Google Doc, Sheet, or Slides link here...",
        label_visibility="collapsed"
    )

with col2:
    if st.button("Add", type="primary", use_container_width=True):
        if new_url:
            doc_type = detect_doc_type(new_url)
            title = extract_title_from_url(new_url, doc_type)
            if add_document(title, new_url, doc_type):
                st.toast("✅ Document added!")
                st.rerun()
            else:
                st.error("Failed to add.")
        else:
            st.warning("Paste a link first.")

st.divider()

# Document gallery
docs_df = get_documents()

if docs_df.empty:
    st.info("No documents yet. Paste a link above to add your first document.")
else:
    # Gallery grid (3 columns)
    cols = st.columns(3)
    
    for idx, row in docs_df.iterrows():
        col = cols[idx % 3]
        
        with col:
            doc_type = row['doc_type']
            icon_svg = ICONS.get(doc_type, ICONS['other'])
            
            # Format date
            created_at = row['created_at']
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime("%b %d")
                else:
                    date_str = "—"
            except:
                date_str = "—"
            
            # Card with icon, title, and link
            card_bg = "#2D2D2D" if is_dark else "#FFFFFF"
            text_color = "#E0E0E0" if is_dark else "#202124"
            muted_color = "#9AA0A6" if is_dark else "#5F6368"
            
            st.markdown(f'''
                <a href="{row['doc_url']}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: {card_bg};
                        border: 1px solid {'#404040' if is_dark else '#E0E0E0'};
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 12px;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        transition: all 0.2s ease;
                        cursor: pointer;
                    " onmouseover="this.style.borderColor='#1A73E8'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.15)';" 
                       onmouseout="this.style.borderColor='{'#404040' if is_dark else '#E0E0E0'}'; this.style.boxShadow='none';">
                        <div style="flex-shrink: 0;">{icon_svg}</div>
                        <div style="flex-grow: 1; min-width: 0;">
                            <div style="color: {text_color}; font-weight: 500; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                {row['title']}
                            </div>
                            <div style="color: {muted_color}; font-size: 12px; margin-top: 2px;">
                                {date_str}
                            </div>
                        </div>
                    </div>
                </a>
            ''', unsafe_allow_html=True)
            
            # Delete option (small popover)
            with st.popover("⋯", use_container_width=False):
                st.caption(f"**{row['title']}**")
                confirm = st.checkbox("Confirm delete", key=f"conf_{row['id']}")
                if confirm:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                        delete_document(row['id'])
                        st.rerun()

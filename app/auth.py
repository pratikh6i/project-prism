"""
Project Prism - Authentication Module
=====================================
Authentication bypass for development.
Replace with actual authentication logic for production.
"""

import streamlit as st

from utils.logger import logger


def check_authentication() -> bool:
    """
    Check if the user is authenticated.
    
    Currently bypassed for development.
    In production, implement proper authentication here.
    
    Returns:
        True if authenticated, False otherwise
    """
    # BYPASS: Always return True for development
    logger.debug("Authentication bypassed (development mode)")
    return True


def login_page() -> None:
    """
    Display the login page.
    Currently shows a placeholder message.
    """
    st.title("🔐 Project Prism - Login")
    
    st.info("""
        **Authentication Bypassed**
        
        This is a development build. In production, this page would 
        display a proper login form with Google Cloud Identity integration.
    """)
    
    if st.button("Continue to Application"):
        st.session_state['authenticated'] = True
        st.rerun()


def logout() -> None:
    """
    Log out the current user.
    """
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    logger.info("User logged out")


def require_auth(func):
    """
    Decorator to require authentication for a page.
    Currently bypassed.
    
    Usage:
        @require_auth
        def my_page():
            st.write("Protected content")
    """
    def wrapper(*args, **kwargs):
        if check_authentication():
            return func(*args, **kwargs)
        else:
            login_page()
            return None
    return wrapper

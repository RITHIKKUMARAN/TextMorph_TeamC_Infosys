

import streamlit as st

# Import core authentication modules
from auth import handle_authentication
from database import register_user, login_user
from ui_components import render_login_ui, render_register_ui

def main():
    """
    Entry point for Streamlit app.
    Currently focused on user authentication integration.
    The main dashboard and other app logic from the 'main' branch
    can be reattached after merging.
    """
    st.set_page_config(page_title="TextMorph | Authentication", layout="wide")
    
    # Handle authentication flow (login/register)
    handle_authentication()

if __name__ == "__main__":
    main()

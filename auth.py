
import streamlit as st
# These imports are now needed here instead of app.py
from ui_components import render_login_ui, render_register_ui
from database import register_user, login_user

def handle_authentication():
    
    # Initialize session state for auth mode if it doesn't exist
    if "mode" not in st.session_state:
        st.session_state.mode = "login"

    # Check query params to switch modes (e.g., from an email link)
    query_params = st.query_params
    if "register" in query_params:
        st.session_state.mode = "register"
        st.query_params.clear()  # Clear query params after use
    elif "login" in query_params:
        st.session_state.mode = "login"
        st.query_params.clear()  # Clear query params after use

    # Render login/register forms based on the current mode
    if st.session_state.mode == "login":
        email, password, login_clicked = render_login_ui()
        if login_clicked:
            # --- Using your placeholder logic ---
            # Replace this with your actual database call:
            # success, msg = login_user(email, password)
            if email and password:
                success, msg = True, "Logged in successfully!"
            else:
                success, msg = False, "Please enter email and password."
            # --- End of placeholder logic ---

            if success:
                st.success(msg)
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.mode = "dashboard"
                st.rerun()  # Use st.rerun to move to the dashboard
            else:
                st.error(msg)

    elif st.session_state.mode == "register":
        email, password, confirm, register_clicked = render_register_ui()
        if register_clicked:
            if password != confirm:
                st.error("Passwords do not match!")
            else:
                # --- Using your placeholder logic ---
                # Replace this with your actual database call:
                # success, msg = register_user(email, password)
                if email and password:
                    success, msg = True, "Registration successful! Please login."
                else:
                    success, msg = False, "Please fill all fields."
                # --- End of placeholder logic ---

                if success:
                    st.success(msg)
                    st.session_state.mode = "login"
                    st.rerun()  # Use st.rerun to go to login page
                else:
                    st.error(msg)
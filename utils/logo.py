import streamlit as st
import base64
import os


def load_custom_css(css_path: str):
    """Load external CSS file for custom Streamlit styling."""
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found at: {css_path}")


def display_logo(logo_path: str):
    """Display app logo with blur and rounded background."""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{encoded_logo}" alt="Logo">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Logo not found at: {logo_path}")

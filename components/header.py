import streamlit as st
import pandas as pd
from utils.logo import get_crypto_logo_url


def render_header(data, selected_name, selected_crypto):
    if data is None or data.empty:
        return

    logo_url = get_crypto_logo_url(selected_name)

    # Get the first letter for fallback
    first_letter = selected_name[0].upper() if selected_name else "?"

    # Create a color based on the crypto name (for fallback)
    import hashlib
    hash_object = hashlib.md5(selected_name.encode())
    hash_hex = hash_object.hexdigest()
    color = f"#{hash_hex[:6]}"

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            padding: 10px 0;
        ">
            <div style="
                height: 48px;
                width: 48px;
                border-radius: 50%;
                overflow: hidden;
                background: white;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid #f0f0f0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <img src="{logo_url}"
                     alt="{selected_name} Logo"
                     onerror="this.onerror=null; this.style.display='none'; this.parentNode.innerHTML += '<div style=\'height:48px;width:48px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:24px;\'>{first_letter}</div>';"
                     style="
                         height: 48px;
                         width: 48px;
                         object-fit: contain;
                         padding: 4px;
                     ">
            </div>
            <span style="
                font-size: 42px;
                font-weight: 700;
                line-height: 1;
                margin: 0;
                color: #1E1E1E;
                letter-spacing: -0.5px;
            ">
                {selected_name}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add a thin divider line
    st.markdown(
        """
        <hr style="
            margin: 5px 0 20px 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
            opacity: 0.3;
            border-radius: 2px;
        ">
        """,
        unsafe_allow_html=True
    )

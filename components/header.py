import streamlit as st
import pandas as pd

from utils.logo import get_crypto_logo_url


def render_header(data, selected_name, selected_crypto):
    if data is None or data.empty:
        return

    logo_url = get_crypto_logo_url(selected_name)

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        ">
            <img src="{logo_url}"
                 alt="{selected_name} Logo"
                 style="
                     height: 36px;
                     width: 36px;
                     border-radius: 50%;
                     margin: 0;
                 ">
            <span style="
                font-size: 36px;
                font-weight: 700;
                line-height: 1;
                margin: 0;
            ">
                {selected_name}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

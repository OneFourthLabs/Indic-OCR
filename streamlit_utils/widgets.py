import os
import base64
import streamlit as st

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    
    # Style courtesy: fabriziovanmarciano.com/button-styles/
    custom_css = f""" 
        <style>
        .dl_button_cont {{
        margin-top: 5px;
        margin-bottom: 5px;
        }}
        .dl_button {{
        color: #494949 !important;
        text-transform: uppercase;
        text-decoration: none;
        background: #ffffff;
        padding: 5px;
        border: 2px solid #494949 !important;
        display: inline-block;
        transition: all 0.4s ease 0s;
        }}
        .dl_button:hover {{
        color: #ffffff !important;
        background: #f6b93b;
        border-color: #f6b93b !important;
        transition: all 0.4s ease 0s;
        text-decoration: none;
        }}
        </style>
    """
    href = custom_css + f'''<div align="center" class="dl_button_cont">
    <a href="data:application/octet-stream;base64,{bin_str}" class="dl_button" download="{os.path.basename(bin_file)}">Download {file_label}</a>
    </div>'''
    return href

def production_mode(page_title=None, favicon='🤖'):
    # Src: docs.streamlit.io/en/stable/api.html#placeholders-help-and-options
    st.beta_set_page_config(page_title=page_title, page_icon=favicon)
    # Src: discuss.streamlit.io/t/how-do-i-hide-remove-the-menu-in-production/362
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    return

import os, sys

INDIC_OCR_PATH = os.environ['INDIC_OCR_HOME']
sys.path.append(INDIC_OCR_PATH)

from ocr_ui import get_configs, get_model, setup_ocr_sidebar, setup_uploader, CONFIGS_PATH, IMAGES_FOLDER, OUTPUT_FOLDER

import streamlit as st
import os

from streamlit_utils.widgets import *
from streamlit_utils.file import *

import streamlit_utils.state

CONFIGS_PATH = os.path.join(INDIC_OCR_PATH, CONFIGS_PATH)
IMAGES_FOLDER = os.path.join(INDIC_OCR_PATH, IMAGES_FOLDER)
OUTPUT_FOLDER = os.path.join(INDIC_OCR_PATH, OUTPUT_FOLDER)

def display_ocr_output(output_path, doc_type='raw'):
    ocr_output_image = st.image(os.path.relpath(output_path) + '.jpg', use_column_width=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.json', 'OCR JSON'), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.jpg', 'OCR Image'), unsafe_allow_html=True)
    
    if doc_type == 'raw':
        return
    
    from rule_based import extract
    data = extract(output_path+'.json', doc_type)
    st.json(data)
    
    return

def setup_ocr_runner(img: io.BytesIO, model):
    st.subheader('Step-2: **OCR and extract document info!**')
    doc_type = st.selectbox('', ['raw', 'pan', 'voter_front', 'voter_back'], index=0)
    latest_progress = st.text('Status: Ready to process')
    progress_bar = st.progress(0.0)
    
    start_button = st.empty()
    start_ocr = start_button.button('Run!')
    if not start_ocr:
        return
    
    start_button.empty()
    latest_progress.text('Status: Processing image')
    img_path = dump_jpeg(img, IMAGES_FOLDER)
    
    progress_bar.progress(0.2)
    latest_progress.text('Status: Running OCR')
    output_path = model.process_img(img_path, OUTPUT_FOLDER)
    
    latest_progress.text('Status: OCR Complete!')
    progress_bar.progress(1.0)
    start_button.button('Clear')
    
    display_ocr_output(output_path, doc_type)
    return

def show_ui(global_state):
    production_mode('Indic OCR GUI - AI4Bharat')
    model = setup_ocr_sidebar(CONFIGS_PATH, global_state)
    uploaded_img = setup_uploader()
    if not uploaded_img:
        return
    setup_ocr_runner(uploaded_img, model)
    return

if __name__ == '__main__':
    global_state = st.get_global_state()
    print('Rerunning UI')
    show_ui(global_state)
    global_state.sync()

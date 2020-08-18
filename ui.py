import os, sys
import streamlit as st

INDIC_OCR_PATH = os.environ['INDIC_OCR_HOME']
sys.path.append(INDIC_OCR_PATH)

from ocr_ui import get_configs, get_model, setup_ocr_sidebar, setup_uploader, display_ocr_output, CONFIGS_PATH, IMAGES_FOLDER, OUTPUT_FOLDER
from streamlit_utils.file import *
from lstm_extractor import extract_with_model
from rule_based import extract

MODELS_FOLDER = "extraction-models"
CONFIGS_PATH = os.path.join(INDIC_OCR_PATH, CONFIGS_PATH)
IMAGES_FOLDER = os.path.join(INDIC_OCR_PATH, IMAGES_FOLDER)
OUTPUT_FOLDER = os.path.join(INDIC_OCR_PATH, OUTPUT_FOLDER)
MODELS_PATH = os.path.join(INDIC_OCR_PATH, MODELS_FOLDER)

def run_extractor(img_path, output_path, doc_type='raw'):   
    if doc_type == 'raw':
        return
    if "LSTM" in doc_type:
        data = extract_with_model(output_path+'.json', doc_type, MODELS_PATH)
    else:
        data = extract(output_path+'.json', doc_type)
    st.json(data)
    return

def setup_ocr_runner(img: io.BytesIO, model):
    st.subheader('Step-2: **OCR and extract document info!**')
    doc_type = st.selectbox('', ['raw', 'pan', 'voter_front', 'voter_back', 'voter_back(LSTM)', 'voter_front(LSTM)', 'pan(LSTM)'], index=0)
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
    
    display_ocr_output(output_path)
    latest_progress.text('Status: OCR Complete! Running Extractor...')
    progress_bar.progress(0.8)
    
    run_extractor(img_path, output_path, doc_type)
    
    latest_progress.text('Status: Extraction Complete!')
    progress_bar.progress(1.0)
    start_button.button('Clear')
    
    return

def show_ui(global_state):
    model = setup_ocr_sidebar(CONFIGS_PATH, global_state)
    uploaded_img = setup_uploader()
    if not uploaded_img:
        return
    setup_ocr_runner(uploaded_img, model)
    return

if __name__ == '__main__':
    # from streamlit_utils.widgets import *
    # production_mode('Indian DocXtract - AI4Bharat')
    import streamlit_utils.state
    global_state = st.get_global_state()
    
    show_ui(global_state)
    global_state.sync()

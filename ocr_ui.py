import streamlit as st
from glob import glob
import os

from streamlit_utils.widgets import *
from streamlit_utils.file import *

CONFIGS_PATH = 'configs/*.json'

IMAGES_FOLDER = os.path.join('images', 'server')
OUTPUT_FOLDER = os.path.join(IMAGES_FOLDER, 'output')
ADDITIONAL_LANGS = ['hi', 'ta']

@st.cache
def get_configs(configs_path_pattern):
    files = glob(configs_path_pattern)
    return[os.path.splitext(os.path.basename(file))[0] for file in files]

# Store a maximum of 1 full OCR model (for now, since it's heavy)
# Disabling mutation check since it uses deep-recursive hasing, hence costly
@st.cache(max_entries=1, allow_output_mutation=True)
def get_model(config_name, configs_path_pattern, langs=None):
    config = configs_path_pattern.replace('*', config_name)
    from indic_ocr.ocr import OCR
    return OCR(config, langs)

def setup_ocr_sidebar(configs_path_pattern):
    st.sidebar.title('OCR Settings')
    
    st.sidebar.subheader('Additional Languages')
    st.sidebar.text('Available Indian languages: ' + str(ADDITIONAL_LANGS))
    extra_langs = st.sidebar.multiselect('Select your Indian language:', ADDITIONAL_LANGS, ADDITIONAL_LANGS[0:1])
    
    st.sidebar.subheader('Config')
    default_config_index = 3
    configs = get_configs(configs_path_pattern)
    config = st.sidebar.selectbox('', configs, index=default_config_index)
    
    model_status = st.sidebar.empty()
    model_status.text('Loading model. Please wait...')
    model = get_model(config, configs_path_pattern, extra_langs)
    model_status.text('Model ready!')
    
    st.sidebar.title('About')
    st.sidebar.text('By AI4Bharat')
    return model

def display_ocr_output(output_path):
    ocr_output_image = st.image(os.path.relpath(output_path + '.jpg'), use_column_width=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.json', 'OCR JSON'), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.jpg', 'OCR Image'), unsafe_allow_html=True)
    return

def setup_ocr_runner(img: io.BytesIO, model):
    st.subheader('Step-2: **OCR!**')
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
    output_path = os.path.abspath(output_path)
    
    latest_progress.text('Status: OCR Complete!')
    progress_bar.progress(1.0)
    start_button.button('Clear')
    
    display_ocr_output(output_path)
    return

def setup_uploader():
    st.title('Indic OCR')
    st.markdown('GUI to perform text detection and recognition')

    st.subheader('Step-1: **Upload your image**')
    st.set_option('deprecation.showfileUploaderEncoding', False)
    uploaded_img = st.file_uploader('', type=['jpg', 'jpeg', 'jfif'])

    show_img = st.empty()
    if not uploaded_img:
        show_img.info('Waiting to upload')
        return None
        
    show_img.image(uploaded_img, caption='Uploaded picture', width=480)
    return uploaded_img

def show_ui():
    model = setup_ocr_sidebar(CONFIGS_PATH)
    uploaded_img = setup_uploader()
    if not uploaded_img:
        return
    setup_ocr_runner(uploaded_img, model)
    return

if __name__ == '__main__':
    production_mode('Indic OCR GUI - AI4Bharat')
    show_ui()

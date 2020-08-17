import streamlit as st
from glob import glob
import os, io
from datetime import datetime

from streamlit_utils.widgets import *
import streamlit_utils.state

global_state = st.get_global_state()

CONFIGS_PATH = 'configs/*.json'

IMAGES_FOLDER = 'images/server/'
OUTPUT_FOLDER = 'images/server/output'
ADDITIONAL_LANGS = ['hi', 'ta']

def dump_jpeg(img: io.BytesIO):
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + '.jpg'
    out_file = os.path.join(IMAGES_FOLDER, out_file)
    with open(out_file, 'wb') as f:
        f.write(img.getbuffer())
    return out_file

@st.cache
def get_configs():
    files = glob(CONFIGS_PATH)
    return[os.path.splitext(os.path.basename(file))[0] for file in files]

# Store a maximum of 1 full OCR model (for now, since it's heavy)
# Disabling mutation check since it uses deep-recursive hasing, hence costly
@st.cache(max_entries=1, allow_output_mutation=True)
def get_model(config_name, langs=None):
    config = CONFIGS_PATH.replace('*', config_name)
    from indic_ocr.ocr import OCR
    return OCR(config, langs)

def show_sidebar():
    st.sidebar.title('OCR Settings')
    
    st.sidebar.subheader('Additional Languages')
    default_extra_langs = global_state.langs if type(global_state.langs) is list else ADDITIONAL_LANGS
    extra_langs = st.sidebar.multiselect('By default, all languages are selected', ADDITIONAL_LANGS, default_extra_langs)
    global_state.langs = extra_langs
    
    st.sidebar.subheader('Config')
    default_config_index = global_state.config_index if type(global_state.config_index) is int else 3
    configs = get_configs()
    config = st.sidebar.selectbox('', configs, index=default_config_index)
    global_state.config_index = configs.index(config)
    
    model_status = st.sidebar.empty()
    model_status.text('Loading model. Please wait...')
    global MODEL
    MODEL = get_model(config, extra_langs)
    model_status.text('Model ready!')
    
    st.sidebar.title('About')
    st.sidebar.text('By AI4Bharat')
    return

def display_ocr_output(output_path):
    ocr_output_image = st.image(output_path + '.jpg', use_column_width=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.json', 'OCR JSON'), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html(output_path+'.jpg', 'OCR Image'), unsafe_allow_html=True)
    return

def show_ocr_runner(img: io.BytesIO):
    st.subheader('Step-2: **OCR!**')
    latest_progress = st.text('Status: Ready to process')
    progress_bar = st.progress(0.0)
    
    start_button = st.empty()
    start_ocr = start_button.button('Run!')
    if not start_ocr:
        return
    
    start_button.empty()
    latest_progress.text('Status: Processing image')
    img_path = dump_jpeg(img)
    
    progress_bar.progress(0.2)
    latest_progress.text('Status: Running OCR')
    output_path = MODEL.process_img(img_path, OUTPUT_FOLDER)
    
    latest_progress.text('Status: OCR Complete!')
    progress_bar.progress(1.0)
    start_button.button('Clear')
    
    display_ocr_output(output_path)
    return

def show_main():
    st.title('Indic OCR')
    st.markdown('GUI to perform text detection and recognition')

    st.subheader('Step-1: **Upload your image**')
    st.set_option('deprecation.showfileUploaderEncoding', False)
    uploaded_img = st.file_uploader('', type=['jpg'])

    show_img = st.empty()
    if not uploaded_img:
        show_img.info('Waiting to upload')
        return
        
    show_img.image(uploaded_img, caption='Uploaded picture', width=480)
    show_ocr_runner(uploaded_img)

def show_ui():
    production_mode('Indic OCR GUI - AI4Bharat')
    show_sidebar()
    show_main()

print('Rerunning UI')
show_ui()
global_state.sync()

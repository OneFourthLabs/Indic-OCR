import streamlit as st
from glob import glob
import os, io
from datetime import datetime
import base64

CONFIGS_PATH = 'configs/*.json'

IMAGES_FOLDER = 'images/server/'
OUTPUT_FOLDER = 'images/server/output'

PRODUCTION = True

def dump_jpeg(img: io.BytesIO):
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + '.jpg'
    out_file = os.path.join(IMAGES_FOLDER, out_file)
    with open(out_file, 'wb') as f:
        f.write(img.getbuffer())
    return out_file

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

@st.cache
def get_configs():
    files = glob(CONFIGS_PATH)
    return[os.path.splitext(os.path.basename(file))[0] for file in files]

# Store a maximum of 1 full OCR model (for now, since it's heavy)
# Disabling mutation check since it uses deep-recursive hasing, hence costly
@st.cache(max_entries=1, allow_output_mutation=True)
def get_model(config_name):
    config = CONFIGS_PATH.replace('*', config_name)
    from indic_ocr.ocr import OCR
    return OCR(config)

def show_sidebar():
    st.sidebar.title('OCR Settings')
    st.sidebar.subheader('Config')
    config = st.sidebar.selectbox('', get_configs(), index=3)
    model_status = st.sidebar.empty()
    model_status.text('Loading model. Please wait...')
    global MODEL
    MODEL = get_model(config)
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

def production_hacks():
    # Src: docs.streamlit.io/en/stable/api.html#placeholders-help-and-options
    st.beta_set_page_config(page_title='Indic OCR GUI - AI4Bharat', page_icon='🤖')
    # Src: discuss.streamlit.io/t/how-do-i-hide-remove-the-menu-in-production/362
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    return

def show_ui():
    if PRODUCTION:
        production_hacks()
    show_sidebar()
    show_main()

print('Rerunning UI')
show_ui()

import os
import json
from enum import Enum
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from uuid import uuid4

from utils.file import dump_uploaded_file

## --------------- Authentication --------------- ##

PRODUCTION_MODE = True

import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials

if PRODUCTION_MODE:
    security = Depends(HTTPBasic())

    # TODO: Use DB for authentication
    with open('credentials.json') as f:
        CREDENTIALS = json.load(f)
else:
    security = None

def authenticate(credentials: HTTPBasicCredentials = security):
    if not PRODUCTION_MODE:
        return True
    
    if credentials.username in CREDENTIALS and secrets.compare_digest(credentials.password, CREDENTIALS[credentials.username]):
        return True # Authenticated!
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect HTTPBasicAuth credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return False

## --------------- OCR Configuration --------------- ##

CONFIGS_PATH = 'configs/*.json'

IMAGES_FOLDER = os.path.join('images', 'server')
OUTPUT_FOLDER = os.path.join(IMAGES_FOLDER, 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class OCR_ConfigName(str, Enum):
    easy_ocr = "easy_ocr"
    google_ocr = "google_ocr"

DEFAULT_CONFIG_NAME = OCR_ConfigName.easy_ocr

from indic_ocr.ocr import OCR
LOADED_MODELS = {}

def get_model(config_name, additional_langs=None):
    code_name = config_name
    if additional_langs:
        additional_langs = sorted(additional_langs)
        code_name += '--' + '_'.join(additional_langs)
    else:
        additional_langs = None
    
    if code_name in LOADED_MODELS:
        return LOADED_MODELS[code_name]
    
    print(f'Loading model {code_name}')
    config = CONFIGS_PATH.replace('*', config_name)
    model = OCR(config, additional_langs)
    
    LOADED_MODELS[code_name] = model
    return model

def perform_ocr(img_path: str, config_name: str, additional_langs=[]):
    ocr = get_model(config_name, additional_langs)
    return ocr.process_img(img_path, None, OUTPUT_FOLDER)

## -------------- API ENDPOINTS -------------- ##

app = FastAPI()

@app.post("/ocr")
async def ocr(is_authenticated: bool = Depends(authenticate),
        image: UploadFile = File(...),
        config: OCR_ConfigName = Form(DEFAULT_CONFIG_NAME),
        additional_langs: list = Form([])):
    
    img_path = dump_uploaded_file(image.filename, image.file, OUTPUT_FOLDER)
    output_path = perform_ocr(img_path, config, additional_langs)
    with open(output_path+'.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/ocr_test")
async def ocr_test(is_authenticated: bool = Depends(authenticate)):
    content = """
<body>
<form action="/ocr" enctype="multipart/form-data" method="post">
<input name="image" type="file" accept="image/*">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

import os
import json
from enum import Enum
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from uuid import uuid4
from datetime import datetime

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
        # Authenticated!
        return True
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

def perform_ocr(file: UploadFile, config_name: str, additional_langs=[]):
    extension = os.path.splitext(file.filename)[1]
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + extension
    img_path = os.path.join(OUTPUT_FOLDER, out_file)
    with open(img_path, 'wb') as f:
        f.write(file.file.read())
    
    ocr = get_model(config_name, additional_langs)
    output_path = ocr.process_img(img_path, None, OUTPUT_FOLDER)
    with open(output_path+'.json', 'r', encoding='utf-8') as f:
        return json.load(f)

## -------------- API ENDPOINTS -------------- ##

app = FastAPI()

@app.post("/ocr")
async def ocr(is_authenticated: bool = Depends(authenticate),
    image: UploadFile = File(...),
    config: OCR_ConfigName = Form(DEFAULT_CONFIG_NAME),
    additional_langs: list = Form([])):
    return perform_ocr(image, config, additional_langs)

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

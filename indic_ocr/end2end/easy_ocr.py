import easyocr
import numpy as np
from indic_ocr.end2end import End2EndOCR_Base

class EasyOCR(End2EndOCR_Base):
    def __init__(self, langs, gpu=False, model_dir=None, args={}):
        self.reader = easyocr.Reader(langs, gpu=gpu, model_storage_directory=model_dir)
        self.args = args
    
    def load_img(self, img_path):
        return easyocr.imgproc.loadImage(img_path)
    
    def run(self, img):
        result = self.reader.readtext(img, **self.args)
        bboxes = []
        for bbox in result:
            bboxes.append({
                'type': 'text',
                'points': np.array(bbox[0]).tolist(),
                'text': bbox[1],
                'confidence': bbox[2]
            })
        return bboxes

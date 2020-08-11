from pytesseract import image_to_string, image_to_data, image_to_osd
import cv2
from indic_ocr.end2end import End2EndOCR_Base
from indic_ocr.recognition.tesseract import TesseractRecognizer
from indic_ocr.utils.lang import get_lang_from_text

class TessarectOCR(End2EndOCR_Base):
    def __init__(self, langs, min_confidence=0.0, psm=3, oem=3):
        self.langs = langs
        self.min_confidence = min_confidence
        self.lang_str = TesseractRecognizer.langs_to_str(langs)
        print('Tessarect setup for languages:', self.lang_str)
        self.config = '--psm %d --oem %d' % (psm, oem)
    
    def preprocess_img(self, img):
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    def run(self, img):
        img = self.preprocess_img(img)
        data = image_to_data(img, lang=self.lang_str, config=self.config, output_type='dict')
        bboxes = []
        for i in range(len(data['text'])):
            text, conf = data['text'][i].strip(), float(data['conf'][i]) / 100.0
            if conf < self.min_confidence or not text:
                continue
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            bboxes.append({
                'type': 'text',
                'points': [ # Clock-wise
                    [x, y], # Left Top
                    [x+w, y], # Right Top
                    [x+w, y+h], # Right Bottom
                    [x, y+h] # Left bottom
                ],
                'width': w,
                'height': h,
                'text': text,
                'confidence': conf,
                'lang': get_lang_from_text(text)
            })
        return bboxes

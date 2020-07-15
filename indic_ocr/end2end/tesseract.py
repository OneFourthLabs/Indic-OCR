from pytesseract import image_to_string, image_to_data, image_to_osd
from PIL import Image, ImageDraw
import numpy as np
from indic_ocr.utils.lang import ISO639_v1_TO_v2, get_lang_from_text
from indic_ocr.end2end import End2EndOCR_Base

class TessarectOCR(End2EndOCR_Base):
    def __init__(self, langs, min_confidence=0.0):
        self.langs = langs
        self.min_confidence = min_confidence
        self.lang_str = []
        # Convert to 3-letter lang codes
        for lang in self.langs:
            if lang in ISO639_v1_TO_v2:
                lang = ISO639_v1_TO_v2[lang]
            self.lang_str.append(lang)
        
        print('Tessarect setup for languages:', self.lang_str)
        self.lang_str = '+'.join(self.lang_str)
    
    def run(self, img):
        data = image_to_data(img, lang=self.lang_str, output_type='dict')
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
    
    def load_img(self, img_path):
        # pytesseract assumes RGB format
        return Image.open(img_path)

    def draw_bboxes(self, img, bboxes, out_img_file):
        # return super().draw_bboxes(np.array(img, dtype=np.uint8), bboxes, out_img_file)
        img_draw = ImageDraw.Draw(img)
        for bbox in bboxes:
            x, y = bbox['points'][0]
            w, h = bbox['width'], bbox['height']
            img_draw.rectangle([(x,y), (x+w, y+h)], outline='rgb(255,0,0)')
            # img_draw.polygon(bbox['points'], outline='rgb(255,0,0)')
            
        img.save(out_img_file)
        return img

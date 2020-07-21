from pytesseract import image_to_string, image_to_data, image_to_osd
import numpy as np
from indic_ocr.utils.lang import ISO639_v1_TO_v2, get_lang_from_text
from indic_ocr.utils.image import np2pil
from indic_ocr.recognition import RecognizerBase

class TesseractRecognizer(RecognizerBase):
    
    @staticmethod
    def langs_to_str(langs):
        # Convert to 3-letter lang codes
        lang_str = []
        for lang in langs:
            if lang in ISO639_v1_TO_v2:
                lang = ISO639_v1_TO_v2[lang]
            lang_str.append(lang)
        return '+'.join(lang_str)
    
    def __init__(self, langs):
        self.langs = langs
        self.lang_str = TesseractRecognizer.langs_to_str(langs)
        print('Tessarect setup for languages:', self.lang_str)
    
    def recognize(self, img):
        if type(img) == np.ndarray:
            img = np2pil(img)
        # TODO: https://github.com/madmaze/pytesseract/issues/286
        final_text = image_to_string(img, lang=self.lang_str).strip()
        if not final_text:
            return {}
        return {
            'text': final_text,
            'lang': get_lang_from_text(final_text)
        }
    
    def recognize_with_confidence(self, img):
        if type(img) == np.ndarray:
            img = np2pil(img)
        data = image_to_data(img, lang=self.lang_str, output_type='dict')
        texts = []
        avg_confidence = 0
        total_bboxes = 0
        # assert len(data['text']) == 1 # Should contain only 1 bbox
        for i in range(len(data['text'])):
            text, conf = data['text'][i].strip(), float(data['conf'][i]) / 100.0
            if conf < 0 or not text:
                continue
            total_bboxes += 1
            avg_confidence += conf
            texts.append(text)
        
        if not total_bboxes:
            return {}
        final_text = ' '.join(texts)
        return {
            'text': final_text,
            'confidence': avg_confidence/total_bboxes,
            'lang': get_lang_from_text(final_text)
        }
    
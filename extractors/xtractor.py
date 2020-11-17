import json

from .lstm_extractor import LSTM_Extractor
from .rule_based import extract
from .qr_extractor import extract_from_qr, QR_DOC_MAP
from .string_rules.str_utils import fix_date, standardize_numerals

from .utils.transliterator import transliterate
BILINGUAL_KEYS_FOR_XLIT = {
    'voter_back': ['address'],
    'voter_front': ['name', 'relation'],
    'aadhar_front': ['name']
}

DATE_KEYS = ['dob', 'doi']

class Xtractor:
    def __init__(self, model_path=None, qr_scanner=None):
        if model_path:
            self.lstm_extractor = LSTM_Extractor(model_path)
        self.qr_scanner = qr_scanner
    
    def extract(self, img_path, extract_type, doc_type, indic_langs, ocr, img_preprocessor=None, output_folder='images/'):
        if self.qr_scanner and doc_type in QR_DOC_MAP:
            qr_bboxes = self.qr_scanner.extract(img_path)
            if qr_bboxes: # If QR extraction is successful, don't run OCR
                result = extract_from_qr(doc_name, qr_bboxes)
                if result:
                    result['logs'] = ['Extracted using QR code']
                    return result
        
        ocr_output_path = ocr.process_img(img_path, img_preprocessor, output_folder)
        return self.process_ocr_json(ocr_output_path+'.json', extract_type, doc_type, indic_langs)

    def process_ocr_json(self, ocr_json_file, extract_type, doc_type, additional_langs=[]):
        lang = 'en'

        with open(ocr_json_file, encoding='utf-8') as f:
            ocr_json = json.load(f)

        if doc_type == 'raw':
            return ocr_json
        elif doc_type == 'pan':
            # PAN has only Hindi text
            lang = 'hi'
        elif additional_langs:
            # Set Indic langauge if any
            i = 0
            while i < len(additional_langs) and lang == 'en':
                lang = additional_langs[i]
                i += 1
        
        data = self.extract_from_ocr(ocr_json, extract_type, doc_type, lang)
        self.post_process(data, doc_type, lang)
        return data
    
    def extract_from_qr(self, doc_type, bboxes):
        data = extract_from_qr(doc_type, bboxes)
        if data:
            data['logs'] = ['Extracted using QR code']
            return data
        else:
            return None
    
    def extract_from_ocr(self, input, extract_type, doc_type, lang):
        bboxes = [bbox for bbox in input['data'] if bbox['type']=='text']
        if not bboxes:
            return {'logs': ['OCR Failed']}
        
        h, w = input['height'], input['width']

        # Pre-processing
        if doc_type == 'voter_front':
            # Remove watermark 'EPIC'
            bboxes = [bbox for bbox in bboxes if not (bbox['text'].startswith('EPI') or bbox['text'].endswith('EPIC'))]

        if "LSTM" in extract_type:
            data = self.lstm_extractor.extract(bboxes, h, w, doc_type, lang)
        else:
            data = extract(bboxes, h, w, doc_type, lang)
        
        return data
    
    def post_process(self, data, doc_type, lang, xlit=True):

        if xlit:
            self.fill_missing_using_xlit(data, doc_type, lang)
        # self.replace_numerals(data, lang)
        self.fix_dates(data)

    def fix_dates(self, data):
        # Sometimes, OCR confuses English numerals with Indic numerals
        # due to errors in training data. Fix it in-place.
        if not 'en' in data:
            return
        
        data = data['en']
        for key in DATE_KEYS:
            if key in data:
                data[key] = fix_date(data[key])
        
        return
    
    def replace_numerals(self, data, lang):
        if not 'en' in data or lang == 'en':
            return
        
        for key, value in data['en'].items():
            data['en'][key] = standardize_numerals(value)
        
        return
    
    def fill_missing_using_xlit(self, result, doc_type, lang):
        if doc_type not in BILINGUAL_KEYS_FOR_XLIT:
            return
        keys = BILINGUAL_KEYS_FOR_XLIT[doc_type]
        
        if not lang in result:
            result[lang] = {}
        if not 'logs' in result:
            result['logs'] = []
        
        for key in keys:
            en_val = result['en'][key] if key in result['en'] else None
            lang_val = result[lang][key] if key in result[lang] else None
            
            if en_val and lang_val:
                # Skip if both are valid
                continue
            
            if en_val:
                lang_val = transliterate('en', lang, en_val)
                result['logs'].append('Transliterated key: %s (from en to %s)' % (key, lang))
                result[lang][key] = lang_val
            
            elif lang_val:
                en_val = transliterate(lang, 'en', lang_val)
                result['logs'].append('Transliterated key: %s (from %s to en)' % (key, lang))
                result['en'][key] = en_val

        return

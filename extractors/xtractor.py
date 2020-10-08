import json

from .lstm_extractor import LSTM_Extractor
from .rule_based import extract
from .qr_extractor import extract_from_qr

from .utils.transliterator import transliterate
BILINGUAL_KEYS_FOR_XLIT = {
    'voter_back': ['address'],
    'voter_front': ['name', 'relation'],
    'aadhar_front': ['name']
}

NUMERALS = {
    'en': '0123456789',
    'hi': '०१२३४५६७८९',
    'ta': '௦௧௨௩௪௫௬௭௮௯'
}

class Xtractor:
    def __init__(self, model_path):
        self.lstm_extractor = LSTM_Extractor(model_path)
    
    def run(self, ocr_json_file, extract_type, doc_type, lang='en'):

        with open(ocr_json_file, encoding='utf-8') as f:
            input = json.load(f)
        
        # TODO: Do not run OCR if QR is successful
        data = extract_from_qr(doc_type, input['data'])
        if data:
            data['logs'] = ['Extracted using QR code']
        else:
            data = self.extract_from_ocr(input, extract_type, doc_type, lang)
        
        self.post_process(data, doc_type, lang)
        return data
    
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

        # Sometimes, OCR confuses English numerals with Indic numerals
        # due to errors in training data. Fix it in-place.
        self.replace_numerals(data, lang)
    
    def replace_numerals(self, data, lang):
        if not 'en' in data or lang == 'en':
            return
        
        if lang in NUMERALS:
            lang_numerals = NUMERALS[lang]
            for key, value in data['en'].items():
                for i, numeral in enumerate(lang_numerals):
                    if not numeral in value:
                        continue
                    value = value.replace(numeral, str(i))
                data['en'][key] = value
        
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

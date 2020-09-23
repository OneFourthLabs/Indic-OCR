import json

from .lstm_extractor import LSTM_Extractor
from .rule_based import extract

class Xtractor:
    def __init__(self, model_path):
        self.lstm_extractor = LSTM_Extractor(model_path)
    
    def run(self, ocr_json_file, extract_type, doc_type, lang='en', write_to=None):

        with open(ocr_json_file, encoding='utf-8') as f:
            input = json.load(f)
        bboxes = input['data']
        bboxes = [bbox for bbox in bboxes if 'text' in bbox]
        if not bboxes:
            return {'logs': ['OCR Failed']}
        
        h, w = input['height'], input['width']

        # Pre-processing
        if doc_type == 'voter_front':
            bboxes = [bbox for bbox in bboxes if not (bbox['text'].startswith('EPIC') or bbox['text'].endswith('EPIC'))]

        if "LSTM" in extract_type:
            data = self.lstm_extractor.extract(bboxes, h, w, doc_type, lang)
        else:
            data = extract(bboxes, h, w, doc_type, lang)

        if write_to:
            with open(write_to, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        return data

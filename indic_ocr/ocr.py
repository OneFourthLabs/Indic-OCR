import json
import os
from tqdm import tqdm

from indic_ocr.utils.image import get_all_images

class OCR:
    def __init__(self, config_json: str,
                 additional_languages: list=None,
                 qr_scan=False):
        
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        
        if additional_languages is not None:
            config['langs'] = ['en'] + additional_languages
        
        self.draw = config['draw'] if 'draw' in config else False
        
        self.qr_scanner = None
        if qr_scan:
            print('Loading QR Scanner')
            from .utils.qr_extractor import QR_Extractor
            self.qr_scanner = QR_Extractor()
        
        print('Loading models using', config_json)
        from indic_ocr.end2end import load_extractor
        self.extractor = load_extractor(config)
        if not self.extractor:
            self.load_models(config)
        print('OCR Loading complete!')

    def load_models(self, config):
        from indic_ocr.detection import load_detector
        detector = load_detector(config)
        
        detect_only = config['recognizer']['disabled'] if 'disabled' in config['recognizer'] else False
        recognizer = None
        if not detect_only:
            from indic_ocr.recognition import load_recognizer
            recognizer = load_recognizer(config)
        
        from indic_ocr.end2end.detect_recog_joiner import DetectRecogJoiner
        self.extractor = DetectRecogJoiner(detector, recognizer)
        return
    
    def process_folder(self, input_folder, preprocessor=None, output_folder=None):
        if not output_folder:
            output_folder = os.path.join(input_folder, 'ocr_output')
        os.makedirs(output_folder, exist_ok=True)
        images = get_all_images(input_folder)
        
        for img_path in tqdm(images, unit=' images'):
            self.process_img(img_path, preprocessor, output_folder)
        
        return
    
    def process_img(self, img_path, preprocessor, output_folder, skip_if_done=False):
        
        # Pre-process image
        if preprocessor:
            img_path = preprocessor.process(img_path, output_folder)
        
        # Check if already processed
        out_file = os.path.join(output_folder, os.path.splitext(os.path.basename(img_path))[0])
        if skip_if_done and os.path.isfile(out_file + '.json'):
            return out_file
        
        # Read image
        # TODO: Currently, each model uses different types of loader. Unify them?
        img = self.extractor.load_img(img_path)
        
        # Run OCR
        bboxes = self.extractor.run(img)
        
        # Run QR Scanner
        if self.qr_scanner:
            qr_bboxes = self.qr_scanner.extract(img_path)
            bboxes.extend(qr_bboxes)
        
        # Save output
        if self.draw:
            img = self.extractor.draw_bboxes(img, bboxes, out_file+'.jpg')
        gt = {
            'data': bboxes,
            'height': img.shape[0],
            'width': img.shape[1],
        } # Add more metadata
        with open(out_file+'.json', 'w', encoding='utf-8') as f:
            json.dump(gt, f, ensure_ascii=False, indent=4)
        return out_file

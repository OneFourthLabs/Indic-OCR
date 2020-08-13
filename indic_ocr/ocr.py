import json
import os, sys
from tqdm import tqdm

from indic_ocr.utils.image import get_all_images

class OCR:
    def __init__(self, config_json):
        print('Loading models using', config_json)
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        
        self.draw = config['draw'] if 'draw' in config else False
        
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
    
    def process(self, input_folder, output_folder=None):
        if not output_folder:
            output_folder = os.path.join(input_folder, 'ocr_output')
        os.makedirs(output_folder, exist_ok=True)
        images = get_all_images(input_folder)
        
        for img_path in tqdm(images, unit=' images'):
            self.process_img(img_path, output_folder)
        
        return
    
    def process_img(self, img_path, output_folder):
        img = self.extractor.load_img(img_path)
        bboxes = self.extractor.run(img)
        out_file = os.path.join(output_folder, os.path.splitext(os.path.basename(img_path))[0])
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

if __name__ == '__main__':
    # TODO: Use click or argparse
    config_json, input_folder = sys.argv[1:3]
    output_folder = sys.argv[3] if len(sys.argv) > 3 else None
    
    OCR(config_json).process(input_folder, output_folder)

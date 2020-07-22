import json
import os, sys
from tqdm import tqdm

from indic_ocr.utils.image import get_all_images

class OCR:
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        
        self.langs = config['langs']
        self.draw = config['draw'] if 'draw' in config else False
        self.detector_name = config['detector']['name']
        self.recognizer_name = config['recognizer']['name']
        
        if self.detector_name == self.recognizer_name == 'tesseract':
            from indic_ocr.end2end.tesseract import TessarectOCR
            self.extractor = TessarectOCR(self.langs,
                                          config['recognizer'].get('min_confidence', 0.1),
                                          psm=config['detector'].get('psm', 3))
        else:
            print('No support for', self.detector_name)
            raise NotImplementedError

    def process(self, input_folder, output_folder=None):
        if not output_folder:
            output_folder = os.path.join(input_folder, 'ocr_output')
        os.makedirs(output_folder, exist_ok=True)
        images = get_all_images(input_folder)
        
        for img_path in tqdm(images, unit=' images'):
            img = self.extractor.load_img(img_path)
            bboxes = self.extractor.run(img)
            out_file = os.path.join(output_folder, os.path.splitext(os.path.basename(img_path))[0])
            gt = {'data': bboxes} # Add more metadata
            with open(out_file+'.json', 'w', encoding='utf=8') as f:
                json.dump(gt, f, ensure_ascii=False, indent=4)
            if self.draw:
                img = self.extractor.draw_bboxes(img, bboxes, out_file+'.jpg')
        
        return

if __name__ == '__main__':
    # TODO: Use click or argparse
    config_json, input_folder = sys.argv[1:3]
    output_folder = sys.argv[3] if len(sys.argv) > 3 else None
    
    OCR(config_json).process(input_folder, output_folder)

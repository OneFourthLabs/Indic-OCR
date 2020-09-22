import sys, os
from indic_ocr.ocr import OCR

if __name__ == '__main__':
    # TODO: Use click or argparse
    config_json, input_path = sys.argv[1:3]
    output_folder = sys.argv[3] if len(sys.argv) > 3 else None
    
    ocr = OCR(config_json) #, preprocessors=['doc_crop'])
    if os.path.isfile(input_path):
        ocr.process_img(input_path, output_folder)
    else:
        ocr.process(input_path, output_folder)

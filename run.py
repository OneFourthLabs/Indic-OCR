import sys, os
from indic_ocr.ocr import OCR

def run(config_json, input_path, output_folder=None, preprocessors=['deskew']):
    ocr = OCR(config_json)
    
    preprocessor = None
    if preprocessors: # Load pre-processor
        if type(preprocessors) == str:
            preprocessors = [preprocessors]
        
        from indic_ocr.utils.img_preprocess import PreProcessor
        preprocessor = PreProcessor(preprocessors)
    
    if os.path.isfile(input_path): # OCR an image
        os.makedirs(output_folder, exist_ok=True)
        ocr.process_img(input_path, preprocessor, output_folder)
    else: # Bulk Inference
        ocr.process_folder(input_path, preprocessor, output_folder)
    
    return

if __name__ == '__main__':
    import fire
    fire.Fire(run)

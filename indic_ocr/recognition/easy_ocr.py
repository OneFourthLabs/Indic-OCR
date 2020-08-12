import easyocr
from indic_ocr.recognition import RecognizerBase

class EasyOCR_Recognizer(RecognizerBase):
    def __init__(self, langs, gpu=False, model_dir=None):
        # WARNING: This is a temporary usage.
        # Ideal thing to do would be just using the recognizer model alone
        self.reader = easyocr.Reader(langs, gpu=gpu, model_storage_directory=model_dir)
        
    def recognize(self, img):
        result = self.reader.readtext(img)
        if not result:
            return {}
        return {
            'text': ' '.join([bbox[1] for bbox in result])
        }

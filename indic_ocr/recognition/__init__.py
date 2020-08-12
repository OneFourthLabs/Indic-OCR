from abc import ABC, abstractmethod

class RecognizerBase(ABC):
    
    @abstractmethod
    def __init__(self, langs):
        pass
    
    @abstractmethod
    def recognize(self, img):
        pass

def load_recognizer(config):
    recognizer_cfg = config['recognizer']
    if recognizer_cfg['name'] == 'tesseract':
        from indic_ocr.recognition.tesseract import TesseractRecognizer
        return TesseractRecognizer(config['langs'], **recognizer_cfg.get('params', {}))
    elif recognizer_cfg['name'] == 'easy_ocr':
        from indic_ocr.recognition.easy_ocr import EasyOCR_Recognizer
        return EasyOCR_Recognizer(config['langs'],
                                  gpu=config.get('gpu', False),
                                  model_dir=config.get('model_dir', None))
    else:
        print('No support for recognizer:', self.recognizer_name)
        raise NotImplementedError
    
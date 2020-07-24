from abc import ABC, abstractmethod

class RecognizerBase(ABC):
    
    @abstractmethod
    def __init__(self, langs):
        pass
    
    @abstractmethod
    def recognize(self, img):
        pass

def load_recognizer(recognizer_cfg, langs=['en']):
    if recognizer_cfg['name'] == 'tesseract':
        from indic_ocr.recognition.tesseract import TesseractRecognizer
        return TesseractRecognizer(langs, **recognizer_cfg.get('params', {}))
    else:
        print('No support for recognizer:', self.recognizer_name)
        raise NotImplementedError
    
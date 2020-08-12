import easyocr
import cv2
from indic_ocr.recognition import RecognizerBase

class EasyOCR_Recognizer(RecognizerBase):
    def __init__(self, langs, gpu=False, model_dir=None):
        # WARNING: This is a temporary usage.
        # Ideal thing to do would be just using the recognizer model alone.
        self.reader = easyocr.Reader(langs, gpu=gpu, model_storage_directory=model_dir)
        self.detector = None
        self.device = 'cuda' if gpu else 'cpu'
        
    def recognize_full(self, img):
        result = self.reader.readtext(img)
        if not result:
            return {}
        return {
            'text': ' '.join([bbox[1] for bbox in result]),
            'confidence': sum([bbox[2] for bbox in result]) / len(result)
        }

    def recognize(self, img):
        # NOTE: Temporary hack to run only the recognizer
        # TODO: https://github.com/JaidedAI/EasyOCR/issues/217
        ratio = img.shape[1]/img.shape[0]
        img = cv2.resize(img, (int(64*ratio), 64), interpolation=cv2.INTER_AREA)
        result = easyocr.recognition.get_text(
            self.reader.character,
            img.shape[0],
            img.shape[1],
            self.reader.recognizer,
            self.reader.converter,
            image_list=[(None, img)],
            device=self.device
        )
        return {
            'text': result[0][1],
            'confidence': result[0][2]
        }

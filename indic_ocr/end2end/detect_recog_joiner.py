from indic_ocr.end2end import End2EndOCR_Base
from indic_ocr.utils.image import crop_image_using_quadrilateral

class DetectRecogJoiner(End2EndOCR_Base):
    def __init__(self, detector, recognizer=None):
        self.detector = detector
        if not recognizer:
            self.run = self.detect
        self.recognizer = recognizer
    
    def detect(self, img):
        return self.detector.detect(img)
    
    def run(self, img):
        bboxes = self.detect(img)
        for bbox in bboxes:
            img_crop = crop_image_using_quadrilateral(img, bbox['points'])
            result = self.recognizer.recognize(img_crop)
            if result:
                bbox.update(result)
        return bboxes
    
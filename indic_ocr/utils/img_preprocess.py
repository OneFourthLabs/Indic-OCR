import os
import cv2

class PreProcessor:
    def __init__(self, processors_list):
        self.processors = []
        for processor_name in processors_list:
            processor = None
            if processor_name == 'remove_bg':
                processor = BG_Remover()
            elif processor_name == 'doc_crop':
                processor = DocAutoCropper()
            
            if processor:
                self.processors.append(processor)
            else:
                print('Unknown pre-processor: ', processor_name)
        
    def process(self, img_path):
        '''
        TODO: Work with cv2 images directly as input & output?
        '''
        for processor in self.processors:
            img_path = processor.process(img_path)
        return img_path
    

from abc import ABC, abstractmethod
class PreProcessorBase(ABC):
    @abstractmethod
    def process(self, img_path):
        pass
    

class BG_Remover(PreProcessorBase):
    from docscan.doc import scan
    
    def process(self, img_path):
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
        
        out_png = BG_Remover.scan(img_bytes)
        out_path = os.path.splitext(img_path)[0] + '-docscan.png'
        
        with open(out_path, 'wb') as f:
            f.write(out_png)
        
        return out_path

class DocAutoCropper(PreProcessorBase):
    import docdetect
    from indic_ocr.utils.image import crop_image_using_quadrilateral, order_points_clockwise

    def process(self, img_path, debug=False):
        img = cv2.imread(img_path)
        rects = self.docdetect.process(img)
        
        if debug:
            out_img = self.docdetect.draw(rects, img)
        else:
            rect = max(rects, key=self.docdetect.processor._area)
            rect = DocAutoCropper.order_points_clockwise(rect)
            out_img = DocAutoCropper.crop_image_using_quadrilateral(img, rect)
        
        out_path = os.path.splitext(img_path)[0] + '-cropped.jpg'
        cv2.imwrite(out_path, out_img)
        return out_path

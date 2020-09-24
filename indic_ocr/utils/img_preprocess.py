import os
import cv2
import numpy as np
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray

class PreProcessor:
    def __init__(self, processors_list):
        self.processors = []
        for processor_name in processors_list:
            processor = None
            if processor_name == 'deskew':
                processor = AutoDeskewer()
            elif processor_name == 'remove_bg':
                processor = BG_Remover()
            elif processor_name == 'doc_crop':
                processor = DocAutoCropper()
            
            if processor:
                self.processors.append(processor)
            else:
                print('Unknown pre-processor: ', processor_name)
        
    def process(self, img_path, out_folder=None):
        '''
        Reads the image, processes it and writes it back
        '''
        img = cv2.imread(img_path)
        for processor in self.processors:
            img = processor.process(img)
        
        if not out_folder:
            out_folder = os.path.dirname(img_path)
        
        out_path = os.path.join(out_folder,
                        os.path.splitext(os.path.basename(img_path))[0]) \
                        + '-preprocessed.jpg'
        cv2.imwrite(out_path, img)
        return out_path
    

from abc import ABC, abstractmethod
class PreProcessorBase(ABC):
    @abstractmethod
    def process(self, img):
        '''
        Assumes cv2 image as input
        '''
        pass
    

class BG_Remover(PreProcessorBase):
    from docscan.doc import scan
    
    def process(self, img):
        status, img_bytes = cv2.imencode('.JPEG', img)
        
        out_png = BG_Remover.scan(img_bytes)
        return cv2.imdecode(np.frombuffer(out_png, dtype='uint8'), cv2.IMREAD_UNCHANGED)

class DocAutoCropper(PreProcessorBase):
    import docdetect
    from indic_ocr.utils.image import crop_image_using_quadrilateral, order_points_clockwise

    def process(self, img):
        rects = self.docdetect.process(img)
        
        rect = max(rects, key=self.docdetect.processor._area)
        rect = DocAutoCropper.order_points_clockwise(rect)
        out_img = DocAutoCropper.crop_image_using_quadrilateral(img, rect)
        
        # if debug: out_img = self.docdetect.draw(rects, img)
        
        return out_img

class AutoDeskewer(PreProcessorBase):
    from deskew import determine_skew
    
    def process(self, img):
        '''
        OpenCV>=3.1 imread by default handles orientation
        if present in EXIF of JPG. Src: stackoverflow.com/a/54929872
        
        TODO: Ensure deskewing is avoided in that case?
        '''
        angle = AutoDeskewer.determine_skew(rgb2gray(img))
        return rotate(img, angle, resize=True) * 255

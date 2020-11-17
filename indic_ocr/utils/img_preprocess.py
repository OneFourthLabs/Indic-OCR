import os
import cv2
from PIL import Image
import numpy as np
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray

class PreProcessor:
    def __init__(self, processors_list):
        self.processors = []
        for processor_name in processors_list:
            processor = None
            if processor_name == 'auto_rotate':
                processor = AutoRotate()
            elif processor_name == 'deskew':
                processor = AutoDeskewer()
            elif processor_name == 'remove_bg':
                processor = BG_Remover()
            elif processor_name == 'doc_crop':
                processor = DocAutoCropper()
            elif processor_name == 'deep_rotate':
                processor = DeepRotate()
            
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
                        + '-output.jpg'
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
        if not angle:
            return img
        return np.array(rotate(img, angle, resize=True) * 255, dtype=np.uint8)

import re
import tempfile
from uuid import uuid4
from .misc import run_command
class AutoRotate2(PreProcessorBase):
    '''
    Inspiration:
    https://stackoverflow.com/questions/56139251
    '''
    
    def get_angle(self, img, min_chars_to_try=100):
        
        # Write the image temporarily
        tmp_file = os.path.join(tempfile.gettempdir(), uuid4().hex + '.jpg')
        cv2.imwrite(tmp_file, img)
        
        output = run_command('tesseract %s - -l eng --psm 0 -c min_characters_to_try=%d' % (tmp_file, min_chars_to_try))
        matches = re.findall('Rotate: \\d+', output)
        # TODO: Also use 'Orientation confidence:'
        if matches:
            # Rotate by this angle counter-clockwise
            angle = matches[0].replace('Rotate: ', '').strip()
            angle = int(angle)
        else:
            angle = 0
        
        try: # Delete the temporary image
            os.remove(tmp_file)
        except OSError:
            pass
            
        return angle
    
    def process(self, img):
        angle = self.get_angle(img)
        # if angle:
        if angle == 90 or angle == 270:
            return rotate(img, angle, resize=True) * 255
        else:
            return img

from pytesseract import image_to_osd
class AutoRotate(PreProcessorBase):
    '''
    TODO: Use this directly as soon as this issue is fixed:
    https://github.com/madmaze/pytesseract/issues/174
    '''
    
    def __init__(self, min_confidence=1.0):
        self.min_confidence = min_confidence
    
    def process(self, img):
        try:
            output = image_to_osd(img, output_type='dict', lang='eng')
        except:
            try:
                output = image_to_osd(img, output_type='dict')
            except:
                return img
        
        if 'orientation' in output and output['orientation'] != 0 and output['orientation_conf'] >= self.min_confidence:
            # angle = (360 - output['rotate']) % 360
            angle = output['orientation']
            # Rotate counter-clockwise by this angle.
            return rotate(img, angle, resize=True) * 255
        else:
            return img

import torch
import torchvision.transforms as transforms
class DeepRotate(PreProcessorBase):
    def __init__(self, model_path='models/DeepRotate/v6.tjm', device=None):
        if os.path.isfile(model_path):
            self.model = torch.jit.load(model_path)
        else:
            exit('Model not found: ' + model_path)
        
        self.device = device
        if not device:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.ANGLES = [0, 90, 180, 270]
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.Grayscale(),
            transforms.ToTensor(),
        ])
        
    def process(self, img):
        input_tensor = self.transform(Image.fromarray(img)).unsqueeze(0).to(self.device)
        output = self.model(input_tensor)
        angle_idx = int(torch.argmax(output[0]))
        if angle_idx:
            return rotate(img, -self.ANGLES[angle_idx], resize=True) * 255
        else:
            return img
        

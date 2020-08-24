import sys, os
sys.path.append(os.path.abspath('libs/clova_ai_recognition'))
from libs.PyTorchOCR.tools.det_infer import DetInfer
from indic_ocr.detection import Detector_Base

import cv2

class DB_Detector(Detector_Base):
    def __init__(self, model_path, max_input_size=736):
        self.model = DetInfer(model_path)
        self.model.resize = MaxResize(max_input_size)
    
    def load_img(self, img_path):
        img = cv2.imread(img_path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    def detect(self, img):
        box_list, score_list = self.model.predict(img, is_output_polygon=False)
        bboxes = []
        for i in range(len(box_list)):
            bboxes.append({
                'type': 'text',
                'confidence': score_list[i],
                'points': box_list[i].tolist()
            })
        
        return bboxes
    

class MaxResize:
    '''
    Modified from: github.com/WenmuZhou/PytorchOCR/blob/f93e47f2ac38e0d3d57065bd87e2f014ee31dc62/torchocr/datasets/det_modules/augment.py#L203
    '''
    
    def __init__(self, short_size):
        """
        :param size: resize尺寸,数字或者list的形式，如果为list形式，就是[w,h]
        :return:
        """
        self.short_size = short_size

    def __call__(self, data: dict) -> dict:
        """
        对图片和文本框进行缩放
        :param data: {'img':,'text_polys':,'texts':,'ignore_tags':}
        :return:
        """
        im = data['img']
        h, w, _ = im.shape
        short_edge = min(h, w)
        if short_edge > self.short_size:
            # 保证短边 >= short_size
            scale = self.short_size / short_edge
            im = cv2.resize(im, dsize=None, fx=scale, fy=scale)
            data['img'] = im
        return data

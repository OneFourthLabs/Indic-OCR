from abc import ABC, abstractmethod
import imageio, cv2
import numpy as np

class Detector_Base(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def detect(self, img):
        pass
    
    def load_img(self, img_path):
        return imageio.imread(img_path)

    def draw_bboxes(self, img, bboxes, out_img_file):
        rect_color = (255,0,0)
        for bbox in bboxes:
            pts = np.array(bbox['points'], np.int32).reshape((-1,1,2))
            img = cv2.polylines(img, [pts], True, rect_color)
            # TODO: Draw confidence and lang near box
        # cv2.imshow(out_img_file, img)
        # cv2.waitKey(0); cv2.destroyAllWindows()
        imageio.imsave(out_img_file, img)
        return img

def load_detector(config):
    detector_cfg = config['detector']
    if detector_cfg['name'] == 'craft':
        from indic_ocr.detection.craft import CRAFT_Detector
        return CRAFT_Detector(detector_cfg.get('params', {}))
    elif detector_cfg['name'] == 'east':
        from indic_ocr.detection.east import EAST_Detector
        return EAST_Detector(**detector_cfg.get('params', {}))
    elif detector_cfg['name'] == 'db':
        from indic_ocr.detection.db import DB_Detector
        return DB_Detector(**detector_cfg.get('params', {}))
    else:
        print('No support for recognizer:', detector_cfg['name'])
        raise NotImplementedError

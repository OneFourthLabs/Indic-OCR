from abc import ABC, abstractmethod 
import numpy as np
import cv2

class End2EndOCR_Base(ABC):
    @abstractmethod
    def __init__(self, langs):
        pass
    
    @abstractmethod
    def run(self, img):
        return []

    @abstractmethod
    def load_img(self, img_path):
        # return imageio.imread(img_path)
        # Each framework seems to be using different formats
        # For now, let's keep it framework dependent
        return None

    @abstractmethod
    def draw_bboxes(self, img, bboxes, out_img_file):
        img = img[..., ::-1] # RGB to BGR for OpenCV
        for bbox in bboxes:
            pts = np.array(bbox['points'], np.int32).reshape((-1,1,2))
            img = cv2.polylines(img, [pts], True, (0,0,255))
            # TODO: Draw text, confidence and lang near box
        # cv2.imshow(out_img_file, img)
        # cv2.waitKey(0); cv2.destroyAllWindows()
        cv2.imwrite(out_img_file, img)
        return img

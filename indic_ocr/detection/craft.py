from craft_text_detector import (
    load_craftnet_model,
    load_refinenet_model,
    get_prediction,
    empty_cuda_cache
)

from indic_ocr.detection import Detector_Base

class CRAFT_Detector(Detector_Base):
    
    def __init__(self, args={}):
        self.refine_net = load_refinenet_model(cuda=args.get('cuda', False))
        self.craft_net = load_craftnet_model(cuda=args.get('cuda', False))
        self.args = args
    
    def detect(self, img):
        prediction_result = get_prediction( image=img,
            craft_net=self.craft_net, refine_net=self.refine_net, **self.args)
        return [{
            'type': 'text',
            'points': points
        } for points in prediction_result['boxes'].tolist()]
    
import numpy as np
import pyboof as pb

pb.init_memmap()

class QR_Extractor:
    def __init__(self):
        self.detector = pb.FactoryFiducial(np.uint8).qrcode()
    
    def extract(self, img_path):
        image = pb.load_single_band(img_path, np.uint8)
        self.detector.detect(image)
        qr_codes = []
        for qr in self.detector.detections:
            qr_codes.append({
                'type': 'qr',
                'text': qr.message,
                'points': [list(vertex) for vertex in qr.bounds.convert_tuple()]
            })
        return qr_codes

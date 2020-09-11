from google.cloud import vision
import os, io
from indic_ocr.end2end import End2EndOCR_Base

class GoogleOCR(End2EndOCR_Base):
    def __init__(self, langs, service_account_json=''):
        #TODO: Use langs
        if service_account_json:
            # Set Credentials
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(service_account_json)
            from google.oauth2.service_account import Credentials
            credentials = Credentials.from_service_account_file(service_account_json)
            
            # Get client
            self.client = vision.ImageAnnotatorClient(credentials=credentials)
            
        else: # Assumes we're running on GCP
            self.client = vision.ImageAnnotatorClient()
        
    
    def load_img(self, img_path):
        '''
        Note: Not a numpy array
        '''
        with io.open(img_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        return {
            'content': image,
            'source': img_path
        }
    
    def run(self, img):
        response = self.client.text_detection(image=img['content'])
        bboxes = []
        for text in response.text_annotations:
            vertices = [ [vertex.x, vertex.y]
                    for vertex in text.bounding_poly.vertices]
            bboxes.append({
                'type': 'text',
                'points': vertices,
                'text': text.description,
                'confidence': 1.0 # Because you're Google?
            })
        # The first is most probably a giant box
        return bboxes[1:]
    
    def draw_bboxes(self, img, bboxes, out_img_file):
        # Any better solution?
        img = super().load_img(img['source'])
        return super().draw_bboxes(img, bboxes, out_img_file)
    
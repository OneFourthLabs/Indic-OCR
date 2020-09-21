import os

class PreProcessor:
    def __init__(self, processors_list):
        self.processors = []
        for processor_name in processors_list:
            processor = None
            if processor_name == 'remove_bg':
                processor = BG_Remover()
            
            if processor:
                self.processors.append(processor)
            else:
                print('Unknown pre-processor: ', processor_name)
        
    def process(self, img_path):
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

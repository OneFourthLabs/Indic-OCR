from abc import ABC, abstractmethod 

class End2EndOCR_Base(ABC):
    @abstractmethod
    def __init__(self, langs):
        pass
    
    @abstractmethod
    def run(self, img, draw=False):
        return []

    @abstractmethod
    def load_img(self, img_path):
        # Each framework seems to be using different formats
        # For now, let's keep it framework dependent
        return None

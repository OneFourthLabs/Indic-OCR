import os

import torch
import torch.nn.functional as F

import numpy as np
from PIL import Image

from indic_ocr.recognition import RecognizerBase


class ClovaAI_Recognizer(RecognizerBase):
    '''
    Inference code based on: github.com/clovaai/deep-text-recognition-benchmark/blob/master/demo.py
    '''
    
    def __init__(self, langs, gpu=False, model_dir=None, args={}):
        self.langs = langs
        self.device = torch.device('cuda' if gpu else 'cpu')
        
        self.set_options(args)
        self.load_characters(model_dir)
        self.load_model(model_dir)
        # opt.saved_model, opt.character
    
    def set_options(self, args):
        default_options = {
            'imgH': 32,
            'imgW': 100,
            'PAD': False,
            'num_fiducial': 20,
            'rgb': False,
            'input_channel': 1,
            'output_channel': 512,
            'hidden_size': 256,
            'num_gpu': torch.cuda.device_count()
        }
        
        for key in default_options:
            if key not in args:
                args[key] = default_options[key]
        
        from munch import munchify
        self.opt = munchify(args)
        return
        
    def load_model(self, root_dir):
        ## --- Load Prediction component --- ##
        opt = self.opt
        if 'CTC' in opt.Prediction:
            from libs.clova_ai_recognition.utils import CTCLabelConverter
            self.converter = CTCLabelConverter(opt.character)
        else:
            from libs.clova_ai_recognition.utils import AttnLabelConverter
            self.converter = AttnLabelConverter(opt.character)
        self.opt.num_class = len(self.converter.character)
        
        ## ---- Data loader ---- ##
        from dataset import AlignCollate
        self.AlignCollate_demo = AlignCollate(imgH=opt.imgH, imgW=opt.imgW, keep_ratio_with_pad=opt.PAD)
        if opt.rgb:
            opt.input_channel = 3
        
        ## --- Load model --- #
        
        model_dir = os.path.join(root_dir, '_'.join(sorted(self.langs)))
        if not os.path.isdir(model_dir):
            exit('ERROR: Model folder %s not found.' % model_dir)
        opt.saved_model = os.path.join(model_dir, 'best_accuracy.pth')
        
        from model import Model
        self.model = torch.nn.DataParallel(Model(opt)).to(self.device)
        
        self.model.load_state_dict(torch.load(opt.saved_model, map_location=self.device))
        self.model.eval()
        return
    
    def load_characters(self, model_dir):
        self.opt.character = []
        if 'en' in self.langs:
            import string
            self.opt.character += list(string.printable) + ['।']
        
        indic_langs = set(self.langs) - set(['en'])
        if not indic_langs:
            return
        
        char_folder = os.path.join(model_dir, 'character_files')
        import pandas as pd
        
        # NOTE: We are sorting here; ensure the same order is true
        for lang in sorted(indic_langs):
            df = pd.read_csv(os.path.join(char_folder, lang) + '.csv')
            unicode_chars = set()
            unicode_glyphs = set()
            for character in df['Character'].values:
                unicode_chars.update(list(character))
            for glyph in df['Glyph'].values:
                unicode_glyphs.update(list(glyph))
            
            self.opt.character += sorted(list(unicode_chars)) + sorted(list(unicode_glyphs))
        
        return
    
    def inference(self, batch):
        with torch.no_grad():
            image_tensors, _ = self.AlignCollate_demo(batch)
            batch_size = image_tensors.size(0)
            image = image_tensors.to(self.device)
            # For max length prediction
            text_for_pred = torch.LongTensor(batch_size, self.opt.batch_max_length + 1).fill_(0).to(self.device)
            
            if 'CTC' in self.opt.Prediction:
                preds = self.model(image, text_for_pred)
                
                # Select max probabilty (greedy decoding) then decode index to character
                preds_size = torch.IntTensor([preds.size(1)] * batch_size)
                _, preds_index = preds.max(2)
                preds_str = self.converter.decode(preds_index, preds_size)
            else:
                preds = self.model(image, text_for_pred, is_train=False)
                
                # Select max probabilty (greedy decoding) then decode index to character
                length_for_pred = torch.IntTensor([self.opt.batch_max_length] * batch_size).to(self.device)
                _, preds_index = preds.max(2)
                preds_str = self.converter.decode(preds_index, length_for_pred)
                
            preds_max_prob, _ = F.softmax(preds, dim=2).max(dim=2)
            result = []
            for pred, pred_max_prob in zip(preds_str, preds_max_prob):
                if 'Attn' in self.opt.Prediction:
                    pred_EOS = pred.find('[s]')
                    pred = pred[:pred_EOS]  # prune after "end of sentence" token ([s])
                    pred_max_prob = pred_max_prob[:pred_EOS]
                # calculate confidence score (= multiply of pred_max_prob)
                confidence_score = pred_max_prob.cumprod(dim=0)[-1]
                result.append((pred, float(confidence_score)))
            
            return result

    def recognize(self, img):
        if type(img) == np.ndarray:
            img = Image.fromarray(img).convert('L')
        result = self.inference([(img, None)])
        return {
            'text': result[0][0],
            'confidence': result[0][1]
        }

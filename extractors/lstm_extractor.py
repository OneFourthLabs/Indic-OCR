
from extractors.lstm.model import Classifier
from PIL import Image
import os
import itertools
import torch
import numpy as np
import string

doc_map = {
    'pan_old': {
        'classes': ['en-dob', 'ignore', 'en-name', 'en-id', 'en-relation'],
        'model': 'pan-model.pt',
    },
    'voter_back': {
        'classes': ['en-address', 'indic-address', 'en-doi', 'en-dob', 'ignore', 'en-gender', 'indic-gender'],
        'model': 'voter-back-model.pt',
    },
    'voter_front': {
        'classes': ['en-relation', 'indic-relation', 'ignore', 'en-name', 'indic-name', 'en-id'],
        'model': 'voter-front-model.pt',
    },
}

def get_model(doc_type, models_path, hidden_dim= 256, num_layers=3, embed_dim=8):
    label_size = len(doc_map[doc_type]['classes'])
    model = Classifier(embed_dim=embed_dim, hidden_dim=hidden_dim,
                    num_layers=num_layers, label_size=label_size)
    model.load_state_dict(torch.load(os.path.join(
        models_path, doc_map[doc_type]['model']), map_location=torch.device('cpu')))
    return model

class LSTM_Extractor:
    def __init__(self, models_path):
        self.models = {}
        for doc in doc_map:
            self.models[doc] = get_model(doc, models_path)


    def get_preds(self, bboxes, texts, target_labels, lang, model):
        preds = model(torch.from_numpy(np.array(bboxes)).unsqueeze(0), device=torch.device("cpu")).squeeze(0)
        max_preds = preds.argmax(dim = 1, keepdim = True)
        reverse_maps = [target_labels[i] for i in max_preds]
        
        key_values, raw = {}, {}
        i = 1
        for text, entity in zip(texts, reverse_maps):
            #Skip strings with punctuations alone
            if all(i in string.punctuation for i in text):
                continue
            if entity == "ignore":
                raw[i] = text
                i+=1
            else:
                if entity in key_values:
                    key_values[entity] = key_values[entity] + " " + text
                else:
                    key_values[entity] = text
        
        # Split the keys into specific lang dicts
        result = {'en': {}, lang: {}}
        for key, value in key_values.items():
            if 'ignore' in key:
                continue
            l, k = key.split('-')
            if l == 'indic':
                l = lang
            result[l][k] = value
        
        # result["key_values"] = key_values
        # result["ignored"] = raw
        
        return result

    def extract(self, input_bboxes, h, w, doc_type, lang):
        texts = []
        bboxes = []
        
        #Unlist the texts and bboxes
        for i in input_bboxes:
            texts.append(i["text"])
            bboxes.append(list(itertools.chain(*i["points"])))

        #Normalize bounding boxes
        for coor in bboxes:
            for i in range(0, 8, 2):
                coor[i] = (coor[i]/w)
                coor[i+1] = coor[i+1]/h
            
        model = self.models[doc_type]
        return self.get_preds(bboxes, texts, doc_map[doc_type]['classes'], lang, model)

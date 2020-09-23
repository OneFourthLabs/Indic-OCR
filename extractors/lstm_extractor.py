
from extractors.lstm.model import Classifier
from PIL import Image
import json, os
import itertools
import torch
import numpy as np
import string

doc_map = {
    'pan': {
        'classes': ['en-dob', 'ignore', 'en-name', 'en-id', 'en-parent'],
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

def get_preds(bboxes, texts, doc_type, lang, model):
    preds = model(torch.from_numpy(np.array(bboxes)).unsqueeze(0), device=torch.device("cpu")).squeeze(0)
    max_preds = preds.argmax(dim = 1, keepdim = True)
    target_labels = doc_map[doc_type]['classes']
    reverse_maps = [target_labels[i] for i in max_preds]
    
    raw = {}
    key_values = {}
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

def extract_with_model(json_file: str, doc_type, lang, models_path, write_to=None):
    with open(json_file, encoding='utf-8') as f:
        input = json.load(f)
        input_bboxes = [bbox for bbox in input['data'] if 'text' in bbox]
        if not input_bboxes:
            return {'Status': 'OCR Failed'}
    
    h, w = input['height'], input['width']
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
          
    model = get_model(doc_type, models_path)
    result = get_preds(bboxes, texts, doc_type, lang, model)
    if write_to:
        with open(write_to, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result

if __name__ == '__main__':
    import fire
    fire.Fire(extract_with_model)

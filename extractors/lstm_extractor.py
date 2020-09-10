
from extractors.lstm.model import Classifier
from PIL import Image
import json, os
import itertools
import torch
import numpy as np
import string

doc_classes_map = {
    'voter_back(LSTM)': ['address_en_value', 'address_indic_value', 'date_value', 'dob_value', 'ignore', 'sex_value_en', 'sex_value_indic'],
    'voter_front(LSTM)': ['father_name_en', 'father_name_indic', 'ignore', 'name_en', 'name_indic', 'voter_id'],
    'pan(LSTM)': ['dob', 'ignore', 'name_en', 'pan_id', 'parent_en']
}

models_name_map = {
    'voter_back(LSTM)': 'voter-back-model.pt',
    'voter_front(LSTM)': 'voter-front-model.pt',
    'pan(LSTM)': 'pan-model.pt'
}

def get_model(doc_type, models_path, hidden_dim= 256, num_layers=3, embed_dim=8):
    label_size = len(doc_classes_map[doc_type])
    model = Classifier(embed_dim=embed_dim, hidden_dim=hidden_dim,
                       num_layers=num_layers, label_size=label_size)
    model.load_state_dict(torch.load(os.path.join(
        models_path, models_name_map[doc_type]), map_location=torch.device('cpu')))
    return model    

def get_preds(bboxes, texts, doc_type, model):
    preds = model(torch.from_numpy(np.array(bboxes)).unsqueeze(0), device=torch.device("cpu")).squeeze(0)
    max_preds = preds.argmax(dim = 1, keepdim = True)
    target_labels = doc_classes_map[doc_type]
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
    result = {}
    result["key_values"] = key_values
    result["ignored"] = raw
    
    return result

def extract_with_model(json_file: str, doc_type, models_path, write_to=None):
    with open(json_file, encoding='utf-8') as f:
        input = json.load(f)
        input = [bbox for bbox in input if 'text' in bbox]
        if not input:
            return {'Status': 'OCR Failed'}
    
    h, w = input['height'], input['width']
    texts = []
    bboxes = []
    
    #Unlist the texts and bboxes
    for i in input["data"]:
        texts.append(i["text"])
        bboxes.append(list(itertools.chain(*i["points"])))

    #Normalize bounding boxes
    for coor in bboxes:
        for i in range(0, 8, 2):
            coor[i] = (coor[i]/w)
            coor[i+1] = coor[i+1]/h
          
    model = get_model(doc_type, models_path)
    result = get_preds(bboxes, texts, doc_type, model)
    if write_to:
        with open(write_to, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result

if __name__ == '__main__':
    import fire
    fire.Fire(extract_with_model)

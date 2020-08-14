import fire
import json
import numpy as np

from extractors import voter_back, voter_front, pan

doc_type_map = {
    'voter_back': voter_back,
    'voter_front': voter_front,
    'pan': pan
}

def get_full_string(sorted_bboxes: list, y_threshold: float = 15):
    full_str = ''
    last_h = sorted_bboxes[0]['points'][0][1]
    for bbox in sorted_bboxes:
        points = np.array(bbox['points'])
        y = bbox['y_mid']
        if abs(last_h-y) > y_threshold:
            full_str += '\n'
        full_str += bbox['text'] + ' '
        last_h = y
    return full_str

def sort_bboxes(bboxes: list, y_threshold=15):
    for bbox in bboxes:
        bbox['x_mid'], bbox['y_mid'] = np.mean(bbox['points'], axis=0)
    for i in range(len(bboxes)-1):
        min_j = i
        for j in range(i+1, len(bboxes)):
            if all((
                bboxes[j]['y_mid'] < bboxes[min_j]['y_mid'],
                abs(bboxes[j]['y_mid'] - bboxes[min_j]['y_mid']) > y_threshold
            )) or all((
                abs(bboxes[j]['y_mid'] - bboxes[min_j]['y_mid']) <= y_threshold,
                bboxes[j]['x_mid'] < bboxes[min_j]['x_mid']
            )):
                min_j = j
        
        if min_j != i:
            bboxes[i], bboxes[min_j] = bboxes[min_j], bboxes[i]
    return bboxes

def extract(json_file: str, doc_type, write_to=None):
    with open(json_file, encoding='utf-8') as f:
        input = json.load(f)
    bboxes = input['data']
    h, w = input['height'], input['width']
    bboxes = sort_bboxes(bboxes)
    full_str = get_full_string(bboxes)
    result = doc_type_map[doc_type].get_values(full_str)
    result['raw'] = full_str.split('\n')
    if write_to:
        with open(write_to, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result

if __name__ == '__main__':
    fire.Fire(extract)

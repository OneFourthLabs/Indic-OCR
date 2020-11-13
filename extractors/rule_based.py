import numpy as np

from .string_rules import voter_back, voter_front, pan_old, pan_new, pan, aadhar_front
from .string_rules.str_utils import standardize_numerals

doc_type_map = {
    'voter_back': voter_back,
    'voter_front': voter_front,
    'pan_old': pan_old,
    'pan_new': pan_new,
    'pan': pan,
    'aadhar_front': aadhar_front
}

def get_full_string(sorted_bboxes: list, y_threshold: float = 0.023):
    full_str = ''
    last_h = sorted_bboxes[0]['points'][0][1]
    for bbox in sorted_bboxes:
        points = np.array(bbox['points'])
        # Skip boxes with H > W
        if 'width' not in bbox:
            bbox['width'] = abs((points[1][0]+points[2][0])/2 - (points[0][0]+points[3][0])/2)
        if 'height' not in bbox:
            bbox['height'] = abs((points[3][1]+points[2][1])/2 - (points[0][1]+points[1][1])/2)
        
        if bbox['height'] > bbox['width']:
            continue
        
        # Decide if same line or new line
        y = bbox['y_mid']
        if abs(last_h-y) > y_threshold:
            full_str += '\n'
        full_str += bbox['text'] + ' '
        last_h = y
    return full_str

def sort_bboxes(bboxes: list, img_width, img_height, y_threshold=0.023):
    for bbox in bboxes:
        bbox['x_mid'], bbox['y_mid'] = np.mean(bbox['points'], axis=0)
        # bbox['y_mid_top'] = np.mean(bbox['points'][:2], axis=0)[1] / img_height
        # bbox['y_mid_bottom'] = np.mean(bbox['points'][2:], axis=0)[1] / img_height
        bbox['x_mid'] /= img_width
        bbox['y_mid'] /= img_height
    for i in range(len(bboxes)-1):
        min_j = i
        for j in range(i+1, len(bboxes)):
            if all((
                bboxes[j]['y_mid'] < bboxes[min_j]['y_mid'],
                abs(bboxes[j]['y_mid'] - bboxes[min_j]['y_mid']) > y_threshold,
                # abs(min(bboxes[j]['y_mid_bottom'], bboxes[min_j]['y_mid_bottom']) - max(bboxes[j]['y_mid_top'], bboxes[min_j]['y_mid_top'])) <= y_threshold
            )) or all((
                abs(bboxes[j]['y_mid'] - bboxes[min_j]['y_mid']) <= y_threshold,
                bboxes[j]['x_mid'] < bboxes[min_j]['x_mid']
            )):
                min_j = j
        
        if min_j != i:
            bboxes[i], bboxes[min_j] = bboxes[min_j], bboxes[i]
    return bboxes

def extract(bboxes, h, w, doc_type, lang):
    
    bboxes = sort_bboxes(bboxes, w, h)
    full_str = get_full_string(bboxes).replace('$', 'S')
    full_str = standardize_numerals(full_str, lang)
    result = doc_type_map[doc_type].get_values(full_str, lang)
    result['raw'] = full_str.split('\n')
    
    return result

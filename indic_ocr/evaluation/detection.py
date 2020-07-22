import json
import os
from glob import glob
from tqdm import tqdm

def json_to_pascalvoc(json_folder, gt_mode=False):
    json_files = glob(os.path.join(json_folder, '*.json'))
    if not json_files:
        exit('No JSON files in ' + json_folder)
    output_folder = os.path.join(json_folder, 'pascal_voc')
    os.makedirs(output_folder, exist_ok=True)
    
    tqdm_str = 'Processing ' + ('groundtruth' if gt_mode else ' detection ') + ' files'
    for json_file in tqdm(json_files, desc=tqdm_str, unit=' images'):
        with open(json_file, encoding='utf-8') as f:
            bboxes = json.load(f)['data']
        
        payload_lines = []
        bboxes = [bbox for bbox in bboxes if bbox['type'] == 'text']
        for bbox in bboxes:
            w, h = bbox['width'], bbox['height'] # Just asserting if they exist because we have to work only with rectangles
            left, top = bbox['points'][0]
            right, bottom = bbox['points'][2]
            # conf = bbox['confidence'] if 'confidence' in bbox else 1.0
            
            if gt_mode:
                payload = '%s %d %d %d %d' % (bbox['type'], left, top, right, bottom)
            else:
                payload = '%s %.5f %d %d %d %d' % (bbox['type'], bbox['confidence'], left, top, right, bottom)
            payload_lines.append(payload)
        
        # Write Pascal VOC txt
        pascal_voc_file = os.path.join(output_folder, os.path.basename(json_file).replace('.json', '.txt'))
        with open(pascal_voc_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(payload_lines))
    
    return len(json_files), output_folder

PASVAL_VOC_EVAL_SCRIPT = 'libs\object_detection_metrics\pascalvoc.py'
def run_pascal_voc_metrics(gt_folder_pascalvoc, pred_folder_pascalvoc):
    print('Computing Pascal VOC metrics...')
    gt = os.path.abspath(gt_folder_pascalvoc)
    det = os.path.abspath(pred_folder_pascalvoc)
    os.system('%s -gt %s -det %s' % (PASVAL_VOC_EVAL_SCRIPT, gt, det))
    return

def eval_detections(gt_folder, prediction_folder):
    gt_count, gt_folder_pascalvoc = json_to_pascalvoc(gt_folder, gt_mode=True)
    pred_count, pred_folder_pascalvoc = json_to_pascalvoc(prediction_folder, gt_mode=False)
    if gt_count != pred_count:
        exit('GT and Predictions count mismatch: %d vs %d' % (gt_count, pred_count))

    run_pascal_voc_metrics(gt_folder_pascalvoc, pred_folder_pascalvoc)

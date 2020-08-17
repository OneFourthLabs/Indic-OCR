import json
import cv2
from tqdm import tqdm
import os
from edit_distance import SequenceMatcher
from collections import Counter
from indic_ocr.utils.image import crop_image_using_quadrilateral, get_all_images
from indic_ocr.recognition import load_recognizer

class RecognizerEval:
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        
        self.recognizer = load_recognizer(config)
    
    def recognize_image(self, img_path):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        gt_path = os.path.splitext(img_path)[0] + '.json'
        if not os.path.isfile(gt_path):
            print('ERROR: No GT file for:', img_path)
            return []
        with open(gt_path, encoding='utf-8') as f:
            bboxes = json.load(f)['data']
        
        bboxes = [bbox for bbox in bboxes if bbox['type'] == 'text']
        outputs, gt = [], []
        for bbox in bboxes:            
            img_crop = crop_image_using_quadrilateral(img, bbox['points'])
            # cv2.imshow(bbox['text'], img_crop)
            # cv2.waitKey(0); cv2.destroyAllWindows()
            result = self.recognizer.recognize(img_crop)
            if not result:
                # print("Failed for: ", bbox['text'])
                result['text'] = ''
            outputs.append(result['text'])
            gt.append(bbox['text'])
        return outputs, gt
    
    def recognize_images(self, image_folder):
        images = get_all_images(image_folder)
        if not images:
            exit('No images in: ' + image_folder)
        outputs, gt_list = [], []
        for image in tqdm(images, desc='Running Recognizer', unit='image'):
            output, gt = self.recognize_image(image)
            if output:
                outputs.extend(output)
            if gt:
                gt_list.extend(gt)
        return outputs, gt_list
    
    # Edit-Distance
    def compute_levenshtein(self, pred, gt, max_levenshtein=5):
        assert len(pred) == len(gt)
        total = len(gt)
        # Maintain the count of each edit-distances
        counter = Counter()
        max_chars = 0
        for ref, hyp in zip(gt, pred):
            max_chars += max(len(ref), len(hyp))
            counter[SequenceMatcher(a=ref, b=hyp).distance()] += 1
        avg_chars = max_chars/total
        
        # Compute accuracy for each edit-distance
        accuracies = [0] * max_levenshtein
        total_dist = 0
        for levenshtein, count in counter.items():
            if levenshtein < max_levenshtein:
                accuracies[levenshtein] = count * 100 / total
            total_dist += levenshtein * count
        
        avg_dist = total_dist/total
        return accuracies, avg_dist, avg_dist/avg_chars
    
    def read_gt_tsv(self, gt_file):
        with open(gt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        images, gt = [], []
        root_dir = os.path.dirname(gt_file)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            image, word = line.split('\t')
            image_path = os.path.join(root_dir, image)
            if not os.path.isfile(image_path):
                print('Skipping:', image_path, '(Not found)')
                continue
            gt.append(word)
            images.append(image_path)
        return images, gt
    
    def eval_tsv(self, gt_file):
        images, gt = self.read_gt_tsv(gt_file)
        outputs = []
        # Run Inference
        for image in tqdm(images, desc='Running recognizer', unit='image'):
            word = self.infer(image)
            outputs.append(word)
        # Dump output to a file
        output_dump = ['IMAGE\tGT\tPREDICTION']
        for i in range(len(images)):
            output_dump.append('%s\t%s\t%s' % (images[i], gt[i], outputs[i]))
        output_tsv = os.path.join(os.path.dirname(gt_file), 'output.tsv')
        with open(output_tsv, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_dump))

        return outputs, gt
    
    def eval_metrics(self, outputs, gt):
        accuracies, avg_dist, norm_dist = self.compute_levenshtein(outputs, gt)
        
        print('Distance\tAccuracy %')
        accuracy_sum = 0
        for edit_dist, accuracy in enumerate(accuracies):
            accuracy_sum += accuracy
            print('%d\t\t%.2f' % (edit_dist, accuracy_sum))
        print('---------------------------')
        print('Averaged Edit Distance: %.2f' % avg_dist)
        print('Normalized Edit Distance: %.4f' % norm_dist)
        return
    
    def eval(self, gt_path):
        if os.path.isfile(gt_path):
            outputs, gt = self.eval_tsv(gt_path)
        elif os.path.isdir(gt_path):
            # Use OCR JSON Ground-Truths
            outputs, gt = self.recognize_images(gt_path)
        else:
            exit('Ground Truth does not exist: ' + gt_path)
        
        self.eval_metrics(outputs, gt)
        return

    def infer(self, img_path):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        result = self.recognizer.recognize(img)
        return result['text'] if result else ''

import json
import imageio, cv2
from glob import glob
from tqdm import tqdm
import os
from edit_distance import SequenceMatcher
from indic_ocr.utils.image import crop_image_using_quadrilateral, get_all_images
from collections import Counter

class RecognizerEval:
    def __init__(self, config_json):
        with open(config_json, encoding='utf-8') as f:
            config = json.load(f)
        
        self.langs = config['langs']
        self.recognizer_name = config['recognizer']['name']
        if self.recognizer_name == 'tesseract':
            from indic_ocr.recognition.tesseract import TesseractRecognizer
            self.recognizer = TesseractRecognizer(self.langs, psm=config['recognizer'].get('psm', 7))
        else:
            print('No support for', self.recognizer_name)
            raise NotImplementedError
        
    
    def recognize_image(self, img_path):
        '''
        Returns an array of tuples of (pred_word, gt_word)
        '''
        img = imageio.imread(img_path)
        gt_path = os.path.splitext(img_path)[0] + '.json'
        if not os.path.isfile(gt_path):
            print('ERROR: No GT file for:', img_path)
            return []
        with open(gt_path, encoding='utf-8') as f:
            bboxes = json.load(f)['data']
        
        bboxes = [bbox for bbox in bboxes if bbox['type'] == 'text']
        outputs = []
        for bbox in bboxes:            
            img_crop = crop_image_using_quadrilateral(img, bbox['points'])
            # cv2.imshow(bbox['text'], img_crop)
            # cv2.waitKey(0); cv2.destroyAllWindows()
            result = self.recognizer.recognize(img_crop)
            if not result:
                # print("Failed for: ", bbox['text'])
                result['text'] = ''
            outputs.append((result['text'], bbox['text']))
        return outputs
    
    def recognize_images(self, image_folder):
        images = get_all_images(image_folder)
        if not images:
            exit('No images in: ' + image_folder)
        outputs = []
        for image in tqdm(images, desc='Running Recognizer', unit=' images'):
            output = self.recognize_image(image)
            if output:
                outputs.extend(output)
        return outputs
    
    # Edit-Distance
    def compute_levenshtein(self, data, max_levenshtein=5):
        counter = Counter()
        for ref, hyp in data:
            counter[SequenceMatcher(a=ref, b=hyp).distance()] += 1
        
        total = len(data)
        accuracies = [0] * max_levenshtein
        total_dist = 0
        for levenshtein, count in counter.items():
            if levenshtein < max_levenshtein:
                accuracies[levenshtein] = count * 100 / total
            total_dist += levenshtein * count
        
        return accuracies, total_dist/total
    
    def eval(self, folder):
        outputs = self.recognize_images(folder)
        accuracies, avg_dist = self.compute_levenshtein(outputs)
        
        print('Average Edit Distance: %.2f' % avg_dist)
        print('---------------------------')
        print('Distance\tAccuracy %')
        accuracy_sum = 0
        for edit_dist, accuracy in enumerate(accuracies):
            accuracy_sum += accuracy
            print('%d\t\t%.2f' % (edit_dist, accuracy_sum))

        return
    
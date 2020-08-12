
import argparse
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='Evaluation Metrics for OCR')
    
    parser.add_argument(
        '-d',
        dest='detection_mode',
        action='store_true',
        help='Detection mode')
    
    parser.add_argument(
        '-r',
        dest='recognition_mode',
        action='store_true',
        help='Recognition mode')
    
    parser.add_argument(
    '-gt',
    '--gtfolder',
    dest='gt_folder',
    help='folder containing your ground truth JSON and images')
    
    parser.add_argument(
    '--gt-txt',
    dest='gt_txt',
    help='TSV file with your ground truth labels and image paths for recognition')
    
    parser.add_argument(
    '-det',
    '--detfolder',
    dest='det_folder',
    default=None,
    help='folder containing your detected bounding boxes JSON files')
    
    parser.add_argument(
    '-cfg',
    '--config',
    dest='config',
    default=None,
    help='config JSON file')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    if args.detection_mode:
        if not args.det_folder:
            exit('Provide --detfolder for detected outputs')
        if not args.gt_folder:
            exit('Provide --gtfolder for ground truth')
        from indic_ocr.evaluation.detection import eval_detections
        eval_detections(args.gt_folder, args.det_folder)
    
    if args.recognition_mode:
        if not args.config:
            exit('Provide --config file')
        gt = args.gt_folder if args.gt_folder else args.gt_txt
        from indic_ocr.evaluation.recognition import RecognizerEval
        RecognizerEval(args.config).eval(gt)

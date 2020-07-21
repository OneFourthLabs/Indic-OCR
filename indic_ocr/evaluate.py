
if __name__ == '__main__':
    import argparse
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
    required=True,
    help='folder containing your ground truth JSON and images')
    
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
    
    args = parser.parse_args()
    
    if args.detection_mode:
        if not args.det_folder:
            exit('Provide --detfolder for detected outputs')
        from indic_ocr.evaluation.detection import eval_detections
        eval_detections(args.gt_folder, args.det_folder)
    
    if args.recognition_mode:
        if not args.config:
            exit('Provide --config file')
        from indic_ocr.evaluation.recognition import RecognizerEval
        RecognizerEval(args.config).eval(args.gt_folder)
    
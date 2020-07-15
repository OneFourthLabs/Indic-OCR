# Indic OCR

## Pre-requisites

- Python 3.7+
- Install [Tessarect OCR](https://github.com/tesseract-ocr/tesseract) with your required languages
- `git clone <repo>` and `cd <repo>`
- `pip install -r dependencies.txt`

## Running OCR

```
python indic_ocr/ocr.py <config.json> <input_folder> [<output_folder>]
```

## Computing Detection Accuracy

```
python indic_ocr/evaluate.py <ground_truth_json_folder> <detections_json_folder>
```

# Indic OCR

## Pre-requisites

- Python 3.7+
- `git clone <repo>` and `cd <repo>`
- `pip install -r dependencies.txt`
- Check [`Installation documentation`](/documentation/Installation.md) to install specific OCR dependencies

## Running OCR

```
python indic_ocr/ocr.py <config.json> <input_folder> [<output_folder>]
```

Check [`configs`](/configs/) folder for sample configs.

# Evaluation

## Computing Detection Scores

```
python indic_ocr/evaluate.py -d -gt <ground_truth_json_folder> -det <detections_json_folder>
```

## Computing Recognition Accuracies

```
python indic_ocr/evaluate.py -r -gt <ground_truth_json_folder> -cfg <config_json_file>
```

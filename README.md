# Indic OCR

## Pre-requisites

- Python 3.7+
- `git clone <repo>` and `cd <repo>`
- `pip install -r dependencies.txt`
- Check [`Installation documentation`](/documentation/Installation.md) to install OCR dependencies/models

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

### Using OCR's JSON Format

```
python indic_ocr/evaluate.py -r -gt <ground_truth_json_folder> -cfg <config_json_file>
```

### Using a TSV file

```
python indic_ocr/evaluate.py -r --gt-txt <ground_truth_tsv> -cfg <config_json_file>
```

Parameters:
- `--gt-txt`: Tab-separated file with each line having `image_path` and corresponding `text_label`

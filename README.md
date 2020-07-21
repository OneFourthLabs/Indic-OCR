# Indic OCR

## Pre-requisites

- Python 3.7+
- `git clone <repo>` and `cd <repo>`
- `pip install -r dependencies.txt`

### Installing [Tessarect OCR](https://github.com/tesseract-ocr/tesseract) with your required languages

- If you're on Linux, best option: `sudo apt-get install tesseract-ocr-all`
- If you're on Windows, use the latest installer [from here](https://github.com/tesseract-ocr/tessdoc/blob/master/Home.md#windows) and install all required languages by choosing that option during installation.
- Ensure it's properly installed by typing `tesseract` on command line.
- To manually get language files, [go here](https://github.com/tesseract-ocr/tessdoc/blob/master/Data-Files.md#updated-data-files-for-version-400-september-15-2017).

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

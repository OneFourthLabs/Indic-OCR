# Indic OCR

## Pre-requisites

- Python 3.7+
- `git clone <repo>` and `cd <repo>`
- `pip install -r dependencies.txt`
- Check [`Installation documentation`](/documentation/Installation.md) to install OCR dependencies/models

## Running OCR

```
python run.py <config.json> <input_folder> [<output_folder> <preprocessors>]
```

Check [`configs`](/configs/) folder for sample configs.

Pre-processors suppported:  
(Most of them are not fully reliable, and order is important)

- `deskew` - To auto-deskew images
- `auto_rotate` - To auto-rotate images
- `doc_crop` - To automatically crop only document region
- `remove_bg` - To automatically erase background from foreground

# Evaluation

## Computing Detection Scores

```
python evaluate.py -d -gt <ground_truth_json_folder> -det <detections_json_folder>
```

## Computing Recognition Accuracies

### Using OCR's JSON Format

```
python evaluate.py -r -gt <ground_truth_json_folder> -cfg <config_json_file>
```

### Using a TSV file

```
python evaluate.py -r --gt-txt <ground_truth_tsv> -cfg <config_json_file>
```

Parameters:
- `--gt-txt`: Tab-separated file with each line having `image_path` and corresponding `text_label`

## Running UI Server

0. Ensure *StreamLit* is installed (`pip install streamlit`)
1. Run `streamlit run ocr_ui.py --server.port 80`

It should automatically open the UI in your browser.

## Running API Server

To host the OCR as an API.

Development mode:
```
uvicorn api_server:app --host 0.0.0.0 --reload
```

Visit http://localhost:8000/docs for API documentation.

Example - Testing the API using Python:

```py
payload = {'additional_langs': ['hi']}
files = {'image': open('your_image.jpg, 'rb')}

response = requests.post('http://localhost:8000/ocr', data=payload, files=files) #auth=('admin', 'pass'))
```

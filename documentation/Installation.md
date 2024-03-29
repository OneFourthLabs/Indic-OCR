# Installing OCR dependencies

- Install the dependencies as required for your inference
- Recommended to use `conda` / `virtualenv` for each type of inference to avoid version lock conflicts.

<hr/>

## End-to-end solutions

### [Tessarect OCR](https://github.com/tesseract-ocr/tesseract)

- If you're on Linux, best option: `sudo apt-get install tesseract-ocr-all`
- If you're on Windows, use the latest installer [from here](https://github.com/tesseract-ocr/tessdoc/blob/master/Home.md#windows) and install all required languages by choosing that option during installation.
- Ensure it's properly installed by typing `tesseract` on command line.
- Then: `pip install pytesseract`
- Optional: To manually get language files, [go here](https://github.com/tesseract-ocr/tessdoc/blob/master/Data-Files.md#updated-data-files-for-version-400-september-15-2017).

### Clova.AI EasyOCR

- Ensure PyTorch is installed (Optional: with CUDA+CuDNN for GPU)
- Install the library:
  - For stable: `pip install easyocr`
  - For latest: `pip install git+https://github.com/JaidedAI/EasyOCR`
- Sample config: [`easy_ocr.json`](/configs/easy_ocr.json)
- [Languages supported](https://github.com/JaidedAI/EasyOCR#supported-languages) | [Parameters allowed](https://github.com/JaidedAI/EasyOCR#readtext-method)

### [Google Vision OCR](https://cloud.google.com/vision/docs/ocr#vision_text_detection-python)

- `pip install google-cloud-vision`
- Sample config: [`google_ocr.json`](/configs/google_ocr.json)
- Ensure to set `service_account_json` path in config if not using GCP
- [Pricing](https://cloud.google.com/vision/pricing)

<hr/>

## Detection

### [CRAFT](https://github.com/clovaai/CRAFT-pytorch)

- `pip install craft-text-detector`
- To run on GPU, install CUDA & CuDNN with corresponding PyTorch.
- Sample config: [`craft+tesseract.json`](/configs/craft+tesseract.json)

### [OpenCV EAST](https://bitbucket.org/tomhoag/opencv-text-detection/) Detector

- Uses OpenCV's DNN Module (CPU Only)
- Sample config: [`east+tesseract.json`](/configs/east+tesseract.json)

### [DB](https://arxiv.org/abs/1911.08947) Text Detector

- Ensure the [PyTorchOCR repo](https://github.com/WenmuZhou/PytorchOCR) is cloned at `libs/PyTorchOCR`.
- Sample config: [`db+tesseract.json`](/configs/db+tesseract.json)

<hr/>

## Recognition

### Custom ClovaAI

- Ensure the [Clova AI repo](https://github.com/clovaai/deep-text-recognition-benchmark/) is cloned at `libs/clova_ai_recognition`.
- (...TODO: Add more )
- Sample config: [`craft+clova_ai.json`](/configs/craft+clova_ai.json)

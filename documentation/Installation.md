# Installing OCR dependencies

Install the dependencies as required.

## Installing [Tessarect OCR](https://github.com/tesseract-ocr/tesseract) with your required languages

- If you're on Linux, best option: `sudo apt-get install tesseract-ocr-all`
- If you're on Windows, use the latest installer [from here](https://github.com/tesseract-ocr/tessdoc/blob/master/Home.md#windows) and install all required languages by choosing that option during installation.
- Ensure it's properly installed by typing `tesseract` on command line.
- To manually get language files, [go here](https://github.com/tesseract-ocr/tessdoc/blob/master/Data-Files.md#updated-data-files-for-version-400-september-15-2017).

## Detection

### Configuring CRAFT

- `pip install craft-text-detector`
- To run on GPU, install CUDA & CuDNN with corresponding PyTorch.
- Sample config: [`craft+tesseract.json`](/configs/craft+tesseract.json)

### Configuring EAST Detector

- Uses OpenCV's DNN Module
- Sample config: [`east+tesseract.json`](/configs/east+tesseract.json)

# Newspaper Scan Processing

Python script to enhance scanned pages from newspaper archive.

![Demo Image](https://github.com/cballenar/enhance-newspaper-scanned-page-via-pil/blob/main/demo.jpg?raw=true)

## What it Does

The script reads a txt file with a list of paths of all the samples to process and for each image:

- Checks the image exists
- Applies high contrast enhancement for OCR
- Reads orientation from OCR version
- Rotates, both, original and OCR version
- Exports Image (text) and Image Data (text + coordinates + confidence) to a txt and json file next to the output image
- Applies a human readable enhancement to the original image
- Saves and closes along with the text files

## Usage
This script assumes some basic knowledge of python and execution of scripts from command line.

1. Install python requirements
1. Add images to process to the `./source` directory.
1. Generate a list of your image paths inside source folder.
    - This can be achieved via `find -f . > image-sources.txt`
    - It will need to be cleaned up to remove unwanted files
1. If appropriate, generate a list of words and convert them to a dawg file and place it in `./training-data/user.lstm-word-dawg`.
    - See [this for documentation](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc) and [this for a tutorial](https://vovaprivalov.medium.com/tesseract-ocr-tips-custom-dictionary-to-improve-ocr-d2b9cd17850b).
1. Ensure the language in the script is what you need. Defaults to Spanish.
1. Run the script `python main.py`.
1. Results will be printed as it progresses. All the images and read texts will be exported to the `./output` directory mirroring the path structure in source.

### Script Variables
- `source_dir` - Defaults to `./source`.
- `output_dir` - Defaults to `./output`. 
- `sources_index_path` - Defaults to `sources-index.txt`.
- `user_words_path` - Defualts to `./training-data/user.lstm-word-dawg`
- `ocr_language` - Defaults to `spa`

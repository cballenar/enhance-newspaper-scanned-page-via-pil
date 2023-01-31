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

## Requirements
This script assumes some basic knowledge of python and execution of scripts from command line.

1. Python (v3.8 confirmed passing)
1. Install Tesseract (v5.2.0 confirmed passing)
1. Install requirements (`pip install -r requirements.txt`)

## Usage

```
main.py [-h] [-f FILE] [-b BATCH] [-s SOURCE] [-o OUTPUT] [-l LANGUAGE] [-w WORDS] [-r] [-d] [-t] [-k] [-m]
```

Results will be printed as it progresses. All the images and read texts will be exported to the `./output` directory mirroring the path structure in source.

### Options

#### `-h`, `--help`
show this help message and exit

#### `-f FILE`, `--File FILE`
Provide path to single image file to process (relative to source), e.g.: `./path/to/file.jpg`

1. Locate the image you want to process, e.g.: `./source/1928/01/01/001-00.jpg`.
1. Execute the command as needed, e.g.: `main.py -f 1928/01/01/001-00.jpg` (notice source default value).

#### `-b BATCH`, `--Batch BATCH`
Provide path to text file containing list of files to process (absolute or relative to script), e.g.: `/full/path/to/file.txt`

1. Add images to process to your source directory, e.g.: `./source`.
1. Generate a list of your image paths inside source folder.
    - This can be achieved via `find -f . > sources.txt`
    - It will need to be cleaned up to remove unwanted files
1. Execute the command as needed, e.g.: `main.py -l sources.txt`

#### `-s SOURCE`, `--Source SOURCE`
Defaults to relative path `./source`
Provide directory path where source image(s) can be found, e.g.: `/full/path/to/output/dir`.

#### `-o OUTPUT`, `--Output OUTPUT`
Defaults to relative path `./output`.
Provide directory path to where output will be saved, e.g.: `/full/path/to/output/dir`. 

Be careful if you're using the same output and source, the original image WILL be overwritten by either the high contrast or the human readable version of the image.

#### `-l`, `--Language`
Provide language to be used by PyTesseract, e.g.: `spa`.
Defaults to `eng`.

#### `-w`, `--Words`
Provide the path to a custom dictionary to improve OCR, e.g.: `./training-data/user.lstm-word-dawg`.
Defaults to blank.

#### `-r`, `--No_Rotate`
Disables OSD Image Rotation of images.

#### `-d`, `--No_Data`
Disables image_text_data generation and output to a `.data.json` file.

#### `-t`, `--No_Text` (Disabled if `-d` flag is provided.)
Disables image_text generation and output to a `.text.txt` file.

#### `-k`, `--No_Keywords` (Disabled if `-d` flag is provided.)
Disables keyword generation and output to a `.words.txt` file.

#### `-m`, `--No_Man_Readable`
Disables generation of a human readable image, and provides a version optimized for OCR.

### Custom Dictionary
If appropriate, generate a list of words and convert them to a dawg file and place it in `./training-data/user.lstm-word-dawg`.
    - See [this for documentation](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc) and [this for a tutorial](https://vovaprivalov.medium.com/tesseract-ocr-tips-custom-dictionary-to-improve-ocr-d2b9cd17850b).

## Examples

Process a single image file (`004-00.jpg`) located in the (`./test`) directory and output the files in the same directory, thus overwriting the image. Use Spanish as the OCR language and the `user.lstm-word-dawg` dictionary file.

```
python main.py -f 004-00.jpg -s test -o test -l spa -w ./training-data/user.lstm-word-dawg
```

Process a batch of images specified in `./sources-index.txt` and located in `./source`, then output the images to the default `./output` directory. Do not roate or output text nor keywords files.

```
python main.py -b sources-index.txt -rtk
```
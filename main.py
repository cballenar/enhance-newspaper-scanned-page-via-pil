from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pytesseract import Output, image_to_osd, image_to_data
import os.path
import logging
import json
import re
import argparse

# Initialize parser
parser = argparse.ArgumentParser(
    description = 'Enhances, rotates, and reads images of scanned archives.'
)

# Adding optional argument
parser.add_argument("-f", "--File",     help = "Provide path to single image file to process (relative to source), e.g.: `./path/to/file.jpg`")
parser.add_argument("-b", "--Batch",    help = "Provide path to text file containing list of files to process (absolute or relative to script), e.g.: `/full/path/to/file.txt`")

parser.add_argument("-s", "--Source",   help = "Provide directory path where source image(s) can be found, e.g.: `/full/path/to/output/dir`. Defaults to relative path `./source`")
parser.add_argument("-o", "--Output",   help = "Provide directory path to where output will be saved, e.g.: `/full/path/to/output/dir`. Defaults to relative path `./output`. Be careful if you're using the same output and source, the original image WILL be overwritten by either the high contrast or the human readable version of the image.")

parser.add_argument("-l", "--Language", help = "Provide language to be used by PyTesseract, e.g.: `eng`. Defaults to `spa`.")
parser.add_argument("-w", "--Words",    help = "Provide the path to a custom dictionary to improve OCR, e.g.: `./training-data/user.lstm-word-dawg`. Defaults to none.")

parser.add_argument("-r", "--No_Rotate",        action="store_true", help = "Disables Auto Rotation of images.")
parser.add_argument("-d", "--No_Data",          action="store_true", help = "Disables image_text_data extraction and output.")
parser.add_argument("-t", "--No_Text",          action="store_true", help = "Disables image_text output. Requires Data extraction.")
parser.add_argument("-k", "--No_Keywords",      action="store_true", help = "Disables keyword output. Requires Data extraction.")
parser.add_argument("-m", "--No_Man_Readable",  action="store_true", help = "Disables generation of a human readable image, and provides a version optimized for OCR.")

# Read arguments from command line
args = parser.parse_args()

source_dir      = args.Source   or "source" # will be joined with the path in the sources index file
output_dir      = args.Output   or "output" # will mirror the paths in the sources index file
ocr_language    = args.Language or "eng"
user_words_path = args.Words    or ""

do_rotate               = False if args.No_Rotate       else True
do_data_extraction      = False if args.No_Data         else True
do_text_extraction      = False if args.No_Text         else True
do_keyword_extraction   = False if args.No_Keywords     else True
do_make_human_readable  = False if args.No_Man_Readable else True

# Configure logs
logging.basicConfig(filename="output.log",level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())

# Build tesseract configuration if available
tess_config = '--user-words {}'.format(user_words_path) if user_words_path else ''

# Profile: Machine Readable - High Contrast
def enhance_high_contrast(image):
    image = image.filter(ImageFilter.UnsharpMask(15,200,18))
    image = ImageOps.autocontrast(image, (17,81))
    image = ImageOps.grayscale(image)
    return image

# Profile: Human Readable
def enhance_readable(image):
    image = image.filter(ImageFilter.GaussianBlur(1))
    image = image.filter(ImageFilter.UnsharpMask(2,150,3))
    image = ImageOps.autocontrast(image, (10,30))
    image = ImageEnhance.Color(image).enhance(0.2)
    return image

# takes an enhanced image, detects its rotation and returns it
# optionally a source image can be passed to also be rotated and returned
# if no path is specified a tmp file will be created
def detect_and_rotate_image(enhanced_image, output_path=os.path.join(output_dir,"tmp.jpg"), source_image=None):
    logging.info("Saving image to attempt to detect orientation...")
    enhanced_image.save(output_path)
    try:
        # ! To fix: Reopen image and read osd
        # this re-opening of the new image from path is currently necessary as osd continues to fail when opening from PIL.
        # See: https://stackoverflow.com/questions/54047116/getting-an-error-when-using-the-image-to-osd-method-with-pytesseract
        osd_results = image_to_osd(output_path, output_type=Output.DICT)
    except Exception as e:
        logging.error(str(e))
        if source_image:
            return enhanced_image, source_image
        return enhanced_image
    else:
        logging.info("Orientation: {} with a {} confidence.".format(osd_results["orientation"],osd_results["orientation_conf"]))
        # If rotation seems good, apply and resave
        if (osd_results["orientation_conf"]>0.75):
            logging.info("Rotating...")
            # apply to high contrast image
            enhanced_image = enhanced_image.rotate(osd_results["orientation"], expand=1)
            # save again if requested
            if not do_make_human_readable:
                enhanced_image.save(output_path)
            # apply to original if available
            if source_image:
                source_image = source_image.rotate(osd_results["orientation"], expand=1)
                return enhanced_image, source_image
    if source_image:
        return enhanced_image, source_image
    return enhanced_image

def extract_text_data_from_image(image, output_path=os.path.join(output_dir,"tmp_data.json")):
    logging.info("Reading data from file...")
    with open(output_path, "w") as image_data_file:
        extracted_data = image_to_data(image, lang=ocr_language, output_type=Output.DICT, config=tess_config)
        image_data_file.write(json.dumps(extracted_data))
    return extracted_data

def extract_text_from_data(data, output_path=os.path.join(output_dir,"tmp_text.txt")):
    logging.info("Extracting texts from data...")
    # place data contents into a structured nested array format that mimics a page
    blocks_array = []
    for index, word in enumerate(data['text']):
        # 
        # check block info and add block if needed
        block_i = data['block_num'][index]
        if ( block_i > len(blocks_array) ): break
        if ( block_i == len(blocks_array) ): blocks_array.append([])
        pars_array = blocks_array[block_i]
        # 
        # check par info and add par if needed
        par_i = data['par_num'][index]
        if ( par_i > len(pars_array) ): break
        if ( par_i == len(pars_array) ): pars_array.append([])
        lines_array = pars_array[par_i]
        # 
        # check line info and add line if needed
        line_i = data['line_num'][index]
        if ( line_i > len(lines_array) ): break
        if ( line_i == len(lines_array) ): lines_array.append([])
        words_array = lines_array[line_i]
        # 
        # add text to line, in par, in block
        words_array.append(word)
    #
    # take structured array and build a single string split into paragraphs
    blocks = []
    for block in blocks_array:
        pars = []
        for par in block:
            lines = []
            for line in par:
                lines.append(' '.join(line).strip())
            pars.append('\n'.join(lines).strip())
        blocks.append('\n'.join(pars).strip())
    text = '\n'.join(blocks).strip()
    #
    # write text to file
    with open(output_path, "w") as image_text_file:
        image_text_file.write(text)
    #
    return text

def extract_keywords_from_data(data, output_path=os.path.join(output_dir,"tmp_keywords.txt")):
    logging.info("Extracting keywords from data...")
    # flatten texts
    text = ' '.join(data['text'])
    text = re.sub("[^\w ]", " ", text)
    text = re.sub("_", " ", text)
    text_words = text.lower().split()
    # extract unique words
    keywords_set = set()
    for word in text_words:
        # check if word contains more than 2 characters, only alpha or only numbers
        if len(word)>1 and (re.match('^[A-Za-z]+$',word) or re.match('^[0-9]+$',word)):
            keywords_set.add(word)
    # cleanup set
    keywords = list(keywords_set)
    keywords.sort()
    # write words to file
    with open(output_path, "w") as image_keywords_file:
        for word in keywords:
            image_keywords_file.write('{}\n'.format(word))
    # return keywords
    return keywords

# Process a Single Image from its path
def process_image(image_path):
    image_path_parts = image_path.split('/')
    image_path_source = os.path.join(source_dir,image_path)
    image_file_name = image_path_parts[-1]
    #
    # validate image
    if (not os.path.exists(image_path_source)):
        logging.warning("Image could NOT be found.")
        return
    #
    # build output path and directory
    image_path_output = os.path.join(output_dir,image_path)
    dir_path_output = os.path.join(output_dir,*image_path_parts[:-1])
    os.makedirs(dir_path_output, exist_ok=True)
    # 
    # format output name of files
    def format_file_name(extension):
        return os.path.join(dir_path_output,image_file_name[:-4]+extension)
    #
    # open Image
    logging.info("Image found...".format(image_path_source))
    image = Image.open(image_path_source)
    #
    # enhance and save image
    high_contrast_image = enhance_high_contrast(image)
    # 
    # perform rotation if requested
    if do_rotate:
        high_contrast_image, image = detect_and_rotate_image(high_contrast_image, image_path_output, image)
    #
    # read data from image
    if do_data_extraction:
        data_file_path = format_file_name(".data.json")
        extracted_data = extract_text_data_from_image(high_contrast_image, data_file_path)
    #
    # read keywords from image
    if do_data_extraction and do_text_extraction:
        extracted_text = extract_text_from_data(extracted_data, format_file_name(".texts.txt"))
    #
    # read keywords from image
    if do_data_extraction and do_keyword_extraction:
        extracted_keywords = extract_keywords_from_data(extracted_data, format_file_name(".words.txt"))
    #
    # enhance original for readability and save as new output
    if do_make_human_readable:
        logging.info("Enhancing original image...")
        image = enhance_readable(image)
        image.save(image_path_output)
    #
    # final cleanup
    high_contrast_image.close()
    image.close()
    logging.info("Done.")

# Process all images in index
def process_images_index(images):
    logging.info("Starting a new batch...")
    with open(images, 'r') as sources_index_file:
        sources_index = sources_index_file.readlines()
        count = 0
        for sources_index_line in sources_index:
            count += 1
            image_path = sources_index_line.strip()
            logging.info("Image {}: {}".format(count, image_path))
            process_image(image_path)

# Call process images index by default when executing from command line
if __name__ == '__main__':
    if args.File:
        process_image(args.File)
    elif args.Batch:
        # List of images
        # This can be gathered via `find -f . > image-sources.txt` and a cleanup
        # TODO: Program gathering of index by searching for files in the source directory
        process_images_index(args.Batch)

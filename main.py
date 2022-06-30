from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pytesseract import Output, image_to_osd, image_to_data, image_to_string
import os.path
import logging
import json

# Script configuration
source_dir = "source" # will be joined with the path in the sources index file
output_dir = "output" # will mirror the paths in the sources index file

sources_index_path = "sources-index.txt"
user_words_path = "./training-data/user.lstm-word-dawg"
ocr_language = "spa"

do_rotate = True
do_text_extraction = True
do_text_data_extraction = True
do_make_human_readable = True # otherwise it will just save the "machine readable" (high contrast grayscale) image

# Configure logs
logging.basicConfig(filename="output.log",level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())

# Build config if available
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
    enhanced_image.save(output_path)
    try:
        # ! To fix: Reopen image and read osd
        # this re-opening of the new image from path is currently necessary as osd continues to fail when opening from PIL.
        # See: https://stackoverflow.com/questions/54047116/getting-an-error-when-using-the-image-to-osd-method-with-pytesseract
        osd_results = image_to_osd(output_path, output_type=Output.DICT)
    except Exception as e:
        logging.error(str(e))
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
    return enhanced_image, source_image

def extract_text_from_image(image, output_path=os.path.join(output_dir,"tmp.txt")):
    logging.info("Reading string from file...")
    with open(output_path, "w") as image_string_file:
        extracted_text = image_to_string(image, lang=ocr_language, config=tess_config)
        image_string_file.write(extracted_text)
    return extracted_text

def extract_data_from_image(image, output_path=os.path.join(output_dir,"tmp.json")):
    logging.info("Reading data from file...")
    with open(output_path, "w") as image_data_file:
        extracted_data = image_to_data(image, lang=ocr_language, output_type=Output.DICT, config=tess_config)
        image_data_file.write(json.dumps(extracted_data))
    return extracted_data

# Process a Single Image from its path
def process_image(image_path):
    image_path_parts = image_path.split('/')
    image_path_source = os.path.join(source_dir,image_path)
    image_file_name = image_path_parts[-1]
    image_exists = os.path.exists(image_path_source)
    if (image_exists):
        logging.info("Image {}: {}".format(count, image_path_source))
        image = Image.open(image_path_source)
        #
        # build output path and directory
        image_path_output = os.path.join(output_dir,image_path)
        dir_path_output = os.path.join(output_dir,*image_path_parts[:-1])
        os.makedirs(dir_path_output, exist_ok=True)
        #
        # enhance and save image
        high_contrast_image = enhance_high_contrast(image)
        # 
        # perform rotation if requested
        if do_rotate:
            high_contrast_image, image = detect_and_rotate_image(high_contrast_image, image_path_output, image)
        #
        # read text from image
        if do_text_extraction:
            text_file_path = os.path.join(dir_path_output,image_file_name[:-4]+"txt")
            extracted_text = extract_text_from_image(high_contrast_image, text_file_path)
        #
        # read data from image
        if do_text_data_extraction:
            data_file_path = os.path.join(dir_path_output,image_file_name[:-4]+"json")
            extracted_data = extract_data_from_image(high_contrast_image, data_file_path)
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
    else:
        logging.warning("Image {}: {} could NOT be found.".format(count, image_path_source))

# Get list of images
# This can be gathered via `find -f . > image-sources.txt` and a cleanup
# TODO: Program gathering of index by searching for files in the source directory
logging.info("Starting a new batch...")
with open(sources_index_path, 'r') as sources_index_file:
    sources_index = sources_index_file.readlines()
    count = 0
    # Strips the newline character
    for sources_index_line in sources_index:
        count += 1
        process_image(sources_index_line.strip())

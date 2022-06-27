from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pytesseract import Output, image_to_osd, image_to_data, image_to_string
import os.path
import json

source_dir = "source" # will be joined with the path in the sources index file
output_dir = "output" # will mirror the paths in the sources index file

sources_index_path = "sources-index.txt"
user_words_path = "./training-data/user.lstm-word-dawg"
ocr_language = "spa"

do_rotate = True
do_text_extraction = True
do_text_data_extraction = True
do_make_human_readable = True # otherwise it will just save the "machine readable" (high contrast grayscale) image

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

# Get list of images
# This can be gathered via `find -f . > image-sources.txt` and a cleanup
# TODO: Program gathering of index by searching for files in the source directory
sources_index_file = open(sources_index_path, 'r')
sources_index = sources_index_file.readlines()
  
count = 0
# Strips the newline character
for image_source in sources_index:
    count += 1
    image_path_parts = image_source.split('/')
    image_path_source = os.path.join(source_dir,image_source.strip())
    image_file_name = image_path_parts[-1]
    image_exists = os.path.exists(image_path_source)
    if (image_exists):
        print("[INFO] Image {}: {}".format(count, image_path_source))
        image = Image.open(image_path_source)
        # build output path and directory
        image_path_output = os.path.join(output_dir,image_source.strip())
        dir_path_output = os.path.join(output_dir,*image_path_parts[:-1])
        os.makedirs(dir_path_output, exist_ok=True)
        # enhance and save image
        high_contrast_image = enhance_high_contrast(image)
        high_contrast_image.save(image_path_output)
        #
        # Perform Rotation if requested
        if do_rotate:
            # ! To fix: Reopen image and read osd
            # this re-opening of the new image from path is currently necessary as osd continues to fail when opening from PIL.
            # See: https://stackoverflow.com/questions/54047116/getting-an-error-when-using-the-image-to-osd-method-with-pytesseract
            osd_results = image_to_osd(image_path_output, output_type=Output.DICT)
            print("[INFO] Orientation: {} with a {} confidence.".format(osd_results["orientation"],osd_results["orientation_conf"]))
            # If rotation seems good, apply and resave
            if (osd_results["orientation_conf"]>0.75):
                print("[INFO] Rotating...")
                # apply to high contrast image
                high_contrast_image = high_contrast_image.rotate(osd_results["orientation"], expand=1)
                high_contrast_image.save(image_path_output)
                # apply to original
                image = image.rotate(osd_results["orientation"], expand=1)
        #
        # read string and data from image
        if do_text_extraction:
            print("[INFO] Reading string from file...")
            image_string_file = open(os.path.join(dir_path_output,image_file_name[:-4]+"txt"), "w")
            image_string_file.write(image_to_string(high_contrast_image, lang=ocr_language, config=tess_config))
            image_string_file.close()
        #
        # read string and data from image
        if do_text_data_extraction:
            print("[INFO] Reading data from file...")
            image_data_file = open(os.path.join(dir_path_output,image_file_name[:-4]+"json"), "w")
            image_data_file.write(json.dumps(image_to_data(high_contrast_image, lang=ocr_language, output_type=Output.DICT, config=tess_config)))
            image_data_file.close()
        # cleanup
        high_contrast_image.close()
        #
        # enhance original for readability, save as new output and close
        if do_make_human_readable:
            print("[INFO] Enhancing original image...")
            image = enhance_readable(image)
            image.save(image_path_output)
        # final cleanup
        image.close()
        print("[INFO] Done.\n")
    else:
        print("[ERROR] Image {}: {} could NOT be found.\n".format(count, image_path_source))

from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pytesseract import Output, image_to_osd, image_to_data, image_to_string
import os.path
import json

source_dir = "samples" # samples/1914/09/06/002-00.jpg
output_dir = "output"

# Profile 5: High Contrast
def enhance_high_contrast(image):
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, (25,60))
    image = image.filter(ImageFilter.UnsharpMask(2,150,3))
    return image

# Profile 6: Readable
def enhance_readable(image):
    image = ImageEnhance.Color(image).enhance(0.2)
    image = ImageOps.autocontrast(image, (10,30))
    image = image.filter(ImageFilter.GaussianBlur(1))
    image = image.filter(ImageFilter.UnsharpMask(2,150,3))
    return image

# Get list of images
# This can be gathered via `find -f . > image-sources.txt` and a cleanup
image_sources_file = open('image-sources.txt', 'r')
image_sources = image_sources_file.readlines()
  
count = 0
# Strips the newline character. Add `[:10]` to only do a sample
for image_source in image_sources:
    count += 1
    image_path_parts = image_source.split('/')
    image_path_source = os.path.join(source_dir,image_source.strip())
    image_file_name = image_path_parts[-1]
    image_exists = os.path.exists(image_path_source)
    if (image_exists):
        print("[INFO] Processing {}: {}".format(count, image_path_source))
        image = Image.open(image_path_source)
        # build output path and directory
        image_path_output = os.path.join(output_dir,image_source.strip())
        dir_path_output = os.path.join(output_dir,*image_path_parts[:-1])
        os.makedirs(dir_path_output, exist_ok=True)
        # enhance and save image
        high_contrast_image = enhance_high_contrast(image)
        high_contrast_image.save(image_path_output)
        #
        # reopen image and read osd
        # this re-opening of the new image from path is currently necessary as osd continues to fail when opening from PIL.
        # See: https://stackoverflow.com/questions/54047116/getting-an-error-when-using-the-image-to-osd-method-with-pytesseract
        osd_results = image_to_osd(image_path_output, output_type=Output.DICT)
        print("[INFO] Orientation: {} with a {} confidence.".format(osd_results["orientation"],osd_results["orientation_conf"]))
        # If rotation seems good, apply and resave
        if (osd_results["orientation_conf"]>0.75):
            # apply to high contrast image
            high_contrast_image = high_contrast_image.rotate(osd_results["orientation"], expand=1)
            high_contrast_image.save(image_path_output)
            # apply to original
            image = image.rotate(osd_results["orientation"], expand=1)
        #
        # read string and data from image
        print("[INFO] Reading string from file")
        image_string_file = open(os.path.join(dir_path_output,image_file_name[:-4]+"txt"), "w")
        image_string_file.write(image_to_string(high_contrast_image, lang='spa'))
        image_string_file.close()
        #
        # read string and data from image
        print("[INFO] Reading data from file")
        image_data_file = open(os.path.join(dir_path_output,image_file_name[:-4]+"json"), "w")
        image_data_file.write(json.dumps(image_to_data(high_contrast_image, lang='spa', output_type=Output.DICT)))
        image_data_file.close()
        # cleanup
        high_contrast_image.close()
        #
        # enhance original for readability, save as new output and close
        print("[INFO] Enhancing original image")
        image = enhance_readable(image)
        image.save(image_path_output)
        image.close()
    else:
        print("[ERROR] Line {}: {} could NOT be found.".format(count, image_path_source))

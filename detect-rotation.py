# As seen in: https://pyimagesearch.com/2022/01/31/correcting-text-orientation-with-tesseract-and-python/
from pytesseract import Output
from PIL import Image
import pytesseract
import argparse
import imutils
import cv2

# construct the argument parser and parse the arguments
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("-i","--image",required=True,help="path to input image to be OCR'd")
args = vars(argument_parser.parse_args())

# load the input image, convert it from BGR to RGB channel ordering,
# and use Tesseract to determine the text orientation

# image = cv2.imread(args["image"])
# rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image = Image.open(args["image"])

results = pytesseract.image_to_osd(image, output_type=Output.DICT,config='--psm 0')

# display the orientation information
print("[INFO] detected orientation: {}".format(results["orientation"]))
print("[INFO] rotate by {} degrees to correct".format(results["rotate"]))
print("[INFO] detected script: {}".format(results["script"]))

# rotate the image to correct the orientation
rotated = imutils.rotate_bound(image, angle=results["rotate"])

# show the original image and output image after orientation
# correction
cv2.imshow("Original", image)
cv2.imshow("Output", rotated)
cv2.waitKey(0)

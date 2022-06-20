from PIL import Image
from PIL import ImageEnhance
from PIL import ImageOps
from PIL import Imagestat
from PIL import ImageFilter
import os

output_dir = "output"
source_dir = "samples"

s1 = "1.jpg"
s2 = "2.jpg"
s3 = "3.jpg"
s4 = "4.jpg"
s5 = "5.jpg"
samples = [s1,s2,s3,s4,s5]

# Profile 5
def profile5(image):
    processed_image = ImageOps.grayscale(image)
    processed_image = ImageOps.autocontrast(processed_image, (25,60))
    processed_image = processed_image.filter(ImageFilter.GaussianBlur(1))
    processed_image = processed_image.filter(ImageFilter.UnsharpMask(2,150,3))
    return processed_image

for i in samples:
    image = Image.open(os.path.join(source_dir,i))
    i_name_parts = image.filename.split('/')
    i_name_parts.remove(source_dir)                # take out source folder
    i_name_parts.insert(0, output_dir)             # add output dir
    i_path = i_name_parts[:-1]                     # take out filename
    i_name = i_name_parts[len(i_name_parts) - 1] # get filename
    print(i_name_parts)
    os.makedirs(os.path.join(*i_path), exist_ok=True)
    i_processed = profile5(i)
    i_processed.save(os.path.join(*i_name_parts))

# # Profile 1
# p1 = ImageEnhance.Brightness(s1).enhance(0.8)
# p1 = ImageEnhance.Color(p1).enhance(0.0)
# p1 = ImageEnhance.Contrast(p1).enhance(6.0)
# p1 = ImageEnhance.Sharpness(p1).enhance(4.0)
# p1.show()

# # Profile 2
# p2 = ImageEnhance.Brightness(s1).enhance(0.8)
# p2 = ImageOps.grayscale(p2)
# p2 = ImageEnhance.Contrast(p2).enhance(6.0)
# p2 = ImageEnhance.Sharpness(p2).enhance(4.0)
# p2.show()

# # Profile 3
# p3 = ImageOps.grayscale(s2)
# p3 = ImageOps.autocontrast(p3, (40,45))
# p3 = p3.filter(ImageFilter.UnsharpMask(2,150,3))
# p3.show()

# Profile 4
# p4 = ImageOps.grayscale(s4)
# p4 = ImageOps.autocontrast(p4, (25,60))
# p4 = p4.filter(ImageFilter.UnsharpMask(2,150,3))
# p4.show()

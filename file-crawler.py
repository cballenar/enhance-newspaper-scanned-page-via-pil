import os.path

source_dir = "samples"
output_dir = "output"

# Using readlines()
image_sources_file = open('image-sources.txt', 'r')
image_sources = image_sources_file.readlines()
  
count = 0
# Strips the newline character
for image_source in image_sources[:10]:
    count += 1
    image_path_parts = image_source.split('/')
    image_path_source = os.path.join(source_dir,image_source.strip())
    image_path_output = os.path.join(output_dir,image_source.strip())
    image_exists = os.path.exists(image_path_source)
    if image_exists:
        print("Line {}: {}".format(count, image_path_source))
        os.makedirs(os.path.join(output_dir,*image_path_parts[:-1]), exist_ok=True)
    else:
        print("ERROR: Line {}: {} could NOT be found.".format(count, image_path_source))

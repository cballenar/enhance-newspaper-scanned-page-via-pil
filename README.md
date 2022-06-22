# Newspaper Scan Processing
Python script to enhance scanned pages from newspaper archive.

The script reads a txt file with a list of paths of all the samples to process and for each image:

- Checks the image exists
- Applies high contrast enhancement
- Reads orientation from high contrast version
- Rotates original and high contrast version
- Saves and closes both versions

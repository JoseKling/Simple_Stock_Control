# Barcode_Reader
An implementation of a barcode reader using only numpy. It was based on the paper 'Robust Recognition of 1-D Barcodes Using Camera Phones', by Steffen Wachenfeld, Sebastian Terlunen and Xiaoyi Jiang. The paper can be found in the following link:  
https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.214.5089&rep=rep1&type=pdf  
I followed the paper as a guide, but since it does not provide the specifics of the algorithm or the code, I had to create it. Of course it is much slower and less precise then the original.  
I divided the implementation in 3 files:
- scanner.py: For capturing video and feeding the algorithm with the line to be scanned.
- processing.py: Processes the image. It basically converts the image to greyscale and performs binarization.
- decoder.py: Takes the binarized image and returns the code.

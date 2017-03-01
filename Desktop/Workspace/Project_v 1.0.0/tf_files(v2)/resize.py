
import cv2
import numpy as np
import os
def reImage():
	img = cv2.imread("capture.jpeg")
	# should be larger than samples / pos pic (so we can place our image on it)
	resized_image = cv2.resize(img, (299, 299))
	cv2.imwrite("capture.jpeg",resized_image)

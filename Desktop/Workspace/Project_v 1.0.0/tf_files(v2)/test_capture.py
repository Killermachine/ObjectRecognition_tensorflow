import cv2
import numpy as np
from resize import reImage
def startCam():
	cap = cv2.VideoCapture(0)

	while True:
		ret, img = cap.read()
		cv2.imshow('img',img)
		k = cv2.waitKey(30) & 0xff
		if k == 27:
			break

		if k == 32:
			cv2.imwrite("capture.jpeg",img)
			# should be larger than samples / pos pic (so we can place our image on it)
			reImage()
	cap.release()
	cv2.destroyAllWindows()

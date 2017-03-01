from test_capture import startCam
from mail import sendResults
from label_image import classifyImage
startCam()
classifyImage()
result = classifyImage()
#print result
sendResults(result)
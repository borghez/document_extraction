import os
import cv2
from tempfile import mkstemp



class CropLayer(object):
	def __init__(self, params, blobs):
		# initialize our starting and ending (x, y)-coordinates of the crop
		self.startX = 0
		self.startY = 0
		self.endX = 0
		self.endY = 0
 
	def getMemoryShapes(self, inputs):
		# the crop layer will receive two inputs -- we need to crop the first input blob to match the shape of the second one, keeping the batch size and number of channels
		(inputShape, targetShape) = (inputs[0], inputs[1])
		(batchSize, numChannels) = (inputShape[0], inputShape[1])
		(H, W) = (targetShape[2], targetShape[3])
		# compute the starting and ending crop coordinates
		self.startX = int((inputShape[3] - targetShape[3]) / 2)
		self.startY = int((inputShape[2] - targetShape[2]) / 2)
		self.endX = self.startX + W
		self.endY = self.startY + H
		# return the shape of the volume (we'll perform the actual crop during the forward pass
		return [[batchSize, numChannels, H, W]]
 
	def forward(self, inputs):
		# use the derived (x, y)-coordinates to perform the crop
		return [inputs[0][:, :, self.startY:self.endY,
				self.startX:self.endX]]
	

	
def DNN(original_image):
	protoPath = os.path.join(os.path.dirname(__file__), "./resources/deploy.prototxt")
	modelPath = os.path.join(os.path.dirname(__file__), "./resources/hed_pretrained_bsds.caffemodel")
	# protoPath = "C:\\Users\\Andrea.Bagante\\Downloads\deploy.prototxt"
	# modelPath = "C:\\Users\\Andrea.Bagante\\Downloads\\hed_pretrained_bsds (1).caffemodel"
	net = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
	cv2.dnn_registerLayer('Crop', CropLayer)

	(H, W) = original_image.shape[:2]

	blob = cv2.dnn.blobFromImage(
		original_image, scalefactor=1.0, size=(W, H),
		mean=(104.00698793, 116.66876762, 122.67891434),
		swapRB=False, crop=False
	)

	net.setInput(blob)
	hed = net.forward()
	hed = cv2.resize(hed[0, 0], (W, H))
	hed = (255 * hed).astype("uint8")
	cv2.dnn_unregisterLayer('Crop')

	temp_file, temp_image_path = mkstemp(suffix=".png")
	with os.fdopen(temp_file, "wb") as f:
		cv2.imwrite(temp_image_path, hed)

	return temp_image_path




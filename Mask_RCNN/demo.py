
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt

# Root directory of the project
ROOT_DIR = os.path.abspath("./")

# Import Mask RCNN
# sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "coco/"))  # To find local version
import coco

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
	print 'downloading trained weights'
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

config = InferenceConfig()
config.display()


# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']


# Load a random image from the images folder
imagepath = sys.argv[1]
file_names = next(os.walk(imagepath))[2]
for filename in file_names:
	if '.jpg' not in filename and '.png' not in filename and '.jpeg' not in filename:
    continue

	print('processing %s' % filename)
	image = skimage.io.imread(os.path.join(imagepath, filename))

	# Run detection
	results = model.detect([image], verbose=1)

	# extract objects
	r = results[0]

	import imageio
	N = r['rois'].shape[0]
	scores = r['scores']
	for i in range(N):
		masked_image = image.copy()
		print(len(image))
		print(len(image[0][0]))
		class_id = r['class_ids'][i]
		score = scores[i] if scores is not None else None
		label = class_names[class_id]
		alpha = 1.0
		mask = r['masks'][:, :, i]
		box = r['rois'][i]
		print(box)
		y1, x1, y2, x2 = box
		# for c in range(3):
		# 	masked_image[:, :, c] = np.where(mask == False,
		# 		0,
		# 		image[:, :, c])
		if len(image[0][0]) == 3:
			masked_image = np.dstack( ( masked_image, np.zeros((len(image), len(image[0])))))

		masked_image[:, :, 3] = np.where(mask == False,
			0,
			255)

		(filefrag, ext) = os.path.basename(filename).split('.')
		ext = 'png'
		newFilename = '%s-%s-%s-%s.%s' % (filefrag, i, label, score, ext)
		print(newFilename)
		#imageio.imwrite(newFilename, masked_image)
		imageio.imwrite('objects/x-' + newFilename, masked_image[y1:y2, x1:x2])


	# visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
	                            # class_names, )
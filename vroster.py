import pickle
import traceback
import sys

import config
from vision.util import CVVideo, Image
from vision.util.Profile import *
from vision.detector import *
from vision.tracker import *
from vision.recognizer.LBPRecognizer import *
from vision.recognizer.BagRecognizer import *
from vision.recognizer.DistRecognizer import *
#from vision.matlab.interface import *
from vision.ui.CVInterface import *
from vision.ai.ip import *
from vision.ai.gap import *

# Setup UI
ui = None
if config.EnableUI == True:
	ui = CVWindow('VRoster')

# Matlab
#matlab = LocalMatlab(config.MatlabVersion, config.MatlabPath, config.MatlabArch)
#matlab.addpath('matlab/')
#matlab.execExpression('addpath(genpath(\'matlab/yalmip\'))')

# Components
video = CVVideo.CVFileVideo(config.TrialMovie)
detector = FastHaarDetector(config.HaarCascade, config.HaarSize)
tracker = TrivialTracker()
ai = GapApproximation()
profile = Profile()

# Recognizer 
recognizers = []
for i in range(0, config.PhotoBag):
	recognizers.append(LBPRecognizer())
recognizers = BagRecognizer(config.PhotoPath, recognizers, config.BoundingBox)

try:
	#while True:
	for i in range(0,40):
		profile.start('FPS')
		
		frame = video.next()
		if frame==None:
			print 'Movie ended!'
			break
		frameGray = Image.toGray(frame)
	
		# Get objects
		profile.start('Haar')
		observations = detector.detect(frameGray)
		profile.end('Haar')
		objects = tracker.update(observations)
		
		objectImages = Image.extractSubImages(frameGray, objects, config.BoundingBox)
	
		# Generate recognition matrix
		recognized = []
		profile.start('LBP')
		for image in objectImages:
			recognized.append(recognizers.query(image))
		profile.end('LBP')
		
		# Attempt to find best matching
		w = numpy.matrix(recognized)
		print numpy.cast[int](w)
		profile.start('IP')
		predicted = ai.predict(w)
		profile.end('IP')
	
		
		print predicted

		if ui != None:
			canvas = CVCanvas(frame)

			for i in range(len(objects)):
				label = predicted[i]
				conf = 0
						
				canvas.drawText('%d ~ %.02f'%(label, conf), (objects[i][0], objects[i][1]-3), (255, 255, 0))
				canvas.drawRect(objects[i], (255,0,0))
			
		
			cv.ShowImage('VRoster', frame)	
			ui.update(canvas)
			
			cv.WaitKey(-1)
		profile.end('FPS')
except KeyboardInterrupt:
	print ''
	profile.stats()
	sys.exit(0)
except Exception as e:
	traceback.print_exc()
	sys.exit(0)
profile.stats()

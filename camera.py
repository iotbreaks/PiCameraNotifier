#!/usr/bin/python
import picamera
import picamera.array
import io
import numpy as np
from pushbullet import Pushbullet
from time import sleep
from push import NotificationHandler
from threading import Thread
from Queue import Queue
from threading import Timer

count =1

class DetectMotion(picamera.array.PiMotionAnalysis):
	def analyse(self,a):
		global isMotionDetected
		global count
		a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
		if(a > 60).sum() > 10:
			isMotionDetected = True
			count+=1
			print("motion detected : ",  count)
		else: 
			isMotionDetected = False


def write_video(stream):
	print('Writing video!')
	with stream.lock:
		for frame in stream.frames:
			if frame.frame_type == picamera.PiVideoFrameType.sps_header:
				stream.seek(frame.position)
				break
		with io.open('/home/pi/Desktop/motion.h264', 'wb') as output:
			output.write(stream.read())

	

########## Main ##########
camera = picamera.PiCamera()
# function1: capturing still image
#camera.capture("/home/pi/Desktop/stillimage.jpg")

# function2: feeding data to motion detection analysis, in port 2
motionAnalysisPort=2
camera.start_recording(
			'/dev/null', 
			splitter_port=motionAnalysisPort,
			resize=(640,480),
			format='h264',
			motion_output=DetectMotion(camera, size=(640,480))
			)
camera.wait_recording(3, splitter_port=motionAnalysisPort)

# function3: recroding HD video to upload and notify
stream = picamera.PiCameraCircularIO(camera, seconds=10)
camera.start_recording(stream,format="h264", splitter_port=1)
camera.wait_recording(10)
camera.stop_recording()
#write_video(stream)
Timer(2,write_video, (stream))

sleep(10)

del camera

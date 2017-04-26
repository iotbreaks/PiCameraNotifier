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
import sched, time

#import NotificationHandler
PUSHBULLET_KEY = 'o.zfBzBeuIf5A5msLDfUK9mlvtwPK8HG0T'	# YOUR API KEY

#========= Global variables ========
isMotionDetected = False
isMotionDetected = False
camera = picamera.PiCamera()
camera.annotate_background = True
stream = picamera.PiCameraCircularIO(camera, seconds=20)
scheduler = sched.scheduler(time.time, time.sleep)
capturedPath = '/home/pi/Desktop/Kenny/PiCameraNotifier/capturedPhotos/'


def didReceiveCommand(command):
	print("didReceiveCommand")
	if command == "check":
		print("get system info")
		print("send notification to response")
		isReceivedCommand = True
	elif command == "last":
		print("get last motion detection info")
		print("send notification to response")
		isReceivedCommand = True
	else: 
		print("Command not supported: " + command)
		print("send notification to response")

print("### Setup Notification Listener")
notificationHandler = NotificationHandler(PUSHBULLET_KEY,didReceiveCommand)

class DetectMotion(picamera.array.PiMotionAnalysis):
	def analyse(self,a):
		global isMotionDetected
		a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
		if(a > 60).sum() > 10:
			print("motion just detected")
			isMotionDetected = True
			motionDetected() 
		else: 
			isMotionDetected = False

def motionDetected():
	print("called When Motion Detected")
	fileName=time.strftime("%Y%m%d_%I:%M:%S%p")  # '20170424_12:53:15AM'
	capture_image(fileName)
	scheduler.enter(1,1, write_video, (fileName,))
	scheduler.run()

def capture_image(fileName):
	global camera
	global notificationHandler
	camera.annotate_text = fileName
	filePath=capturedPath+fileName+'.jpg'
	print("capture still image")
	camera.capture(filePath)
	notificationHandler.pushNotificationToMobile(filePath)

def write_video(fileName):
	global stream
	global notificationHandler
	print('Writing video!')
	with stream.lock:
		for frame in stream.frames:
			if frame.frame_type == picamera.PiVideoFrameType.sps_header:
				stream.seek(frame.position)
				break
		filePath=capturedPath+fileName+'.h264'
		with io.open(filePath, 'wb') as output:
			output.write(stream.read())
		notificationHandler.pushNotificationToMobile(filePath)

def cameraInitialize():
	print("cameraInitialize: for (1) motion detection, and (2) circularIO recording")
	global camera
	# for motion detection 
	motionAnalysisPort=2
	camera.start_recording(
				'/dev/null', 
				splitter_port=motionAnalysisPort,
				resize=(640,480),
				format='h264',
				motion_output=DetectMotion(camera, size=(640,480))
				)
	# for circularIO recording
	HDVideoRecordPort=1
	global stream
	camera.start_recording(
				stream,
				format="h264", 
				splitter_port=HDVideoRecordPort)
	
def main():
	global isMotionDetected
	global isReceivedCommand
	global notificationHandler
	print("### Initialize Camera")
	cameraInitialize()

if __name__ == "__main__":
    main()

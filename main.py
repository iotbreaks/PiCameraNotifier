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
stream = picamera.PiCameraCircularIO(camera, seconds=20)
scheduler = sched.scheduler(time.time, time.sleep)

def didMotionDetected():
	print("capture still image")
	print("Upload image and notify")
	print("Record video within a few seconds")
	print("still moving ?")
	print("upload video and notify")

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
	print("capture still image")
	camera.capture('/home/pi/Desktop/'+fileName+'.jpg')
	

def write_video(fileName):
	global stream
	print('Writing video!')
	with stream.lock:
		for frame in stream.frames:
			if frame.frame_type == picamera.PiVideoFrameType.sps_header:
				stream.seek(frame.position)
				break
		with io.open(fileName+'.h264', 'wb') as output:
			output.write(stream.read())

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
	print("### Setup Notification Listener")
	notificationHandler = NotificationHandler(PUSHBULLET_KEY,didReceiveCommand)
	notificationHandler.pushNotificationToMobile("/home/pi/Desktop/image1.jpg")
	print("### Initialize Camera")
	cameraInitialize()

if __name__ == "__main__":
    main()

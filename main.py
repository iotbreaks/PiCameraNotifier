#!/usr/bin/python
import picamera
import picamera.array
import io
import random
import numpy as np
from pushbullet import Pushbullet
from time import sleep
from push import NotificationHandler



#import NotificationHandler
PUSHBULLET_KEY = 'o.zfBzBeuIf5A5msLDfUK9mlvtwPK8HG0T'	# YOUR API KEY

#========= Global variables ========
isMotionDetected = False

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
	elif command == "last":
		print("get last motion detection info")
		print("send notification to response")
	else: 
		print("Command not supported: " + command)
		print("send notification to response")

def write_video(stream):
	print('Writing video!')
	with stream.lock:
		for frame in stream.frames:
			if frame.frame_type == picamera.PiVideoFrameType.sps_header:
				stream.seek(frame.position)
				break
		with io.open('motion.h264', 'wb') as output:
			output.write(stream.read())

class DetectMotion(picamera.array.PiMotionAnalysis):
	def analyse(self,a):
		global isMotionDetected
		a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
		if(a > 60).sum() > 10:
			isMotionDetected = True
		else: 
			isMotionDetected = False

def cameraInitialize():
	with picamera.PiCamera() as camera:
		with DetectMotion(camera) as output:
			camera.resolution = (640, 480)
			camera.start_recording('/dev/null', format='h264', motion_output=output)
			camera.wait_recording(30)
			camera.stop_recording()
	
 

def main():
	global isMotionDetected
	print("### Setup Notification Listener")
	notificationHandler = NotificationHandler(PUSHBULLET_KEY,didReceiveCommand)
	print("### Initialize Camera")
	cameraInitialize()
	
	while True: 
		if isMotionDetected:
			while isMotionDetected: # wait until no motion anymore
				print("### Capture still image") 
				print("### Upload image and send notification") 
				print("### Record video a few seconds more") 
			print("### Upload video and send notification") 
		elif isReceivedCommand: 
			if command=='check':
				print("### ") 
			elif command == 'last':
				print("### ") 
			else:
				print("### ") 
		else:
			print("### Nothing happens") 
		print("### End of while loop") 

def record_video():
	print("record video")
	with picamera.PiCamera() as camera:
		stream = picamera.PiCameraCircularIO(camera,seconds=20)
		camera.start_recording(stream, format='h264')
		camera.wait_recording(1)
		try:
			while True:
				if isMotionDetected:
					print("count = %d")
					with DetectMotion(camera) as output:
						camera.resolution = (640, 480)
						camera.start_recording(stream, format='h264', motion_output=output)
						camera.wait_recording(10)
						camera.stop_recording()
						write_video(stream)
		finally:
			camera.stop_recording()

if __name__ == "__main__":
    main()

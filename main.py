#!/usr/bin/python
import picamera
import picamera.array
import subprocess
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
#camera = picamera.PiCamera()
#camera.annotate_background = True
#stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera=""
stream=""
scheduler = sched.scheduler(time.time, time.sleep)
capturedPath = '/home/pi/Desktop/Kenny/PiCameraNotifier/'
WORKING_DIR="/home/pi/Desktop/Kenny/PiCameraNotifier/"

def didReceiveCommand(command):
	global notificationHandler
	if command == "@check":
		print("get system info")
		process = subprocess.Popen([ WORKING_DIR + 'systemInfo.sh'], stdout=subprocess.PIPE)
		out, err = process.communicate()
		pushData = {'type': 'TEXT_MESSAGE', 'text': out}
		notificationHandler.pushToMobile(pushData)
	if command == "@snap"	:
		fileName=time.strftime("%Y%m%d_%I:%M:%S%p")  # '20170424_12:53:15AM'
		capture_image(fileName)
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
			didDetectMotion() 
		else: 
			isMotionDetected = False

def didDetectMotion():
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
	print("capture still image to file: ", filePath)
	camera.capture(filePath)
	pushData = {'type': 'FILE_MESSAGE', 'filePath': filePath}
	notificationHandler.pushToMobile(pushData)

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
		pushData = {'type': 'FILE_MESSAGE', 'filePath': filePath}
		notificationHandler.pushToMobile(pushData)

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
	global notificationHandler
	#print("### Initialize Camera")
	#cameraInitialize()

if __name__ == "__main__":
    main()

#!/usr/bin/python
import picamera
import picamera.array
import subprocess
import io
import os
import numpy as np
from pushbullet import Pushbullet
from time import sleep
from push import NotificationHandler
from threading import Thread
from Queue import Queue
import sched, time
import logging

#========= Customisable Parameters ======
#PUSHBULLET_KEY='enter_your_pushbullet_key_here'
PUSHBULLET_KEY = 'o.FjzdLl1ufpMuOuWD7WQmnOZVKrTiM1vP' 

#========= Global variables ========
CAMERA_OUT_PATH = '/home/pi/Desktop/'
WORKING_DIR="/home/pi/Desktop/PiCameraNotifier/"
LOG_FILE_PATH=WORKING_DIR+'run.log'
VIDEO_RECORDING_PORT=1
MOTION_ANALYSIS_PORT=2
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename=LOG_FILE_PATH,level=logging.INFO)
logging.info("=========== app launched ========")

camera = picamera.PiCamera()
camera.annotate_background = True
stream = picamera.PiCameraCircularIO(camera, seconds=10, bitrate=1300000) # estimated base on H.264 encoded data per frame
scheduler = sched.scheduler(time.time, time.sleep)

def didReceiveCommand(command):
	global notificationHandler
	if command == "@check":
		logging.info("get system info")
		process = subprocess.Popen([ WORKING_DIR + 'systemInfo.sh'], stdout=subprocess.PIPE)
		out, err = process.communicate()
		pushData = {'type': 'TEXT_MESSAGE', 'text': out}
		notificationHandler.pushToMobile(pushData)
	if command == "@snap"	:
		fileName=time.strftime("%Y%m%d_%I:%M:%S%p")  # '20170424_12:53:15AM'
		captureImage(fileName)
	else: 
		logging.info("Command not supported: " + command)
		logging.info("send notification to response")
logging.info("### Setup Notification Listener")
notificationHandler = NotificationHandler(PUSHBULLET_KEY,didReceiveCommand)

class DetectMotion(picamera.array.PiMotionAnalysis):
	def analyse(self,a):
		a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
		if(a > 60).sum() > 10:
			logging.info("motion just detected")
			print("motion just detected")
			didDetectMotion()	

isRecordingMotion = False
def didDetectMotion():
		global isRecordingMotion
		if isRecordingMotion:
			print("is Recording Motion ...")
		else: 
			isRecordingMotion = True
			print("start Recording Motion ...")
			global notificationHandler
			global camera
			pushData = {'type': 'TEXT_MESSAGE', 'text': 'Hey! someone sneak into your room. Check it out!'}
			notificationHandler.pushToMobile(pushData)
			fileName=time.strftime("%Y%m%d_%I:%M:%S%p")  # '20170424_12:53:15AM'
			logging.info("push image...")
			captureImage(fileName)
			camera.wait_recording(7)
			writeVideo(fileName)
			isRecordingMotion = False

def captureImage(fileName):
	global camera
	global notificationHandler
	camera.annotate_text = fileName
	filePath=CAMERA_OUT_PATH+fileName+'.jpg'
	logging.info("capture still image to file: ", filePath)
	camera.capture(filePath)
	pushData = {'type': 'IMAGE_MESSAGE', 'filePath': filePath, 'fileName': fileName+'.jpg'}
	logging.info("push image data :", pushData)
	notificationHandler.pushToMobile(pushData)

def writeVideo(fileName):
	global stream
	global notificationHandler
	logging.info('Writing video with fileName: ', fileName)
	filePath=CAMERA_OUT_PATH+fileName+'.h264'
	with stream.lock:
		stream.copy_to(filePath)
	# convert from h264 to mp4
	outputFilePath=CAMERA_OUT_PATH+fileName+'.mp4'
	logging.info("convert from h264 to mp4...")
	subprocess.check_call(["ffmpeg", '-framerate', '24', '-i', filePath, '-c', 'copy', outputFilePath])
	pushData = {'type': 'VIDEO_MESSAGE', 'filePath': outputFilePath, 'fileName': fileName+'.mp4'}
	notificationHandler.pushToMobile(pushData)


def cameraInitialize():
	logging.info("cameraInitialize: for (1) motion detection, and (2) circularIO recording")
	global camera
	# for motion detection 
	camera.start_recording(
				'/dev/null', 
				splitter_port=MOTION_ANALYSIS_PORT,
				resize=(640,480),
				format='h264',
				motion_output=DetectMotion(camera, size=(640,480))
				)
	# for circularIO recording
	global stream
	camera.start_recording(
				stream,
				format="h264", 
				resize=(640,480),
				splitter_port=VIDEO_RECORDING_PORT)
	
def main():
	logging.info("Start main")
	global notificationHandler
	logging.info("### Initialize Camera")
	cameraInitialize()
	pushData = {'type': 'TEXT_MESSAGE', 'text': 'PiCameraNotifier app starts !'}
	notificationHandler.pushToMobile(pushData)
			

if __name__ == "__main__":
    main()

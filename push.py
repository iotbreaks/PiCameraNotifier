#!/usr/bin/env python
from pushbullet import Listener
from pushbullet import Pushbullet
from threading import Thread
from Queue import Queue
from time import sleep
import os
import logging

HTTP_PROXY_HOST = None
HTTP_PROXY_PORT = None
QUEUE_MAX_SIZE = 0 # NO LIMIT
NUM_THREAD = 1 # Limit the concurrent thead to 1

class NotificationHandler:
	def __init__(self, pushBulletAPIKey,didReceiveCommand):
		# Setup pushBullet manager	
		self.pushBulletAPIKey = pushBulletAPIKey
		self.didReceiveCommand = didReceiveCommand
		self.pushBulletManager = Pushbullet(self.pushBulletAPIKey)
		thread = Thread(target = self.__createListener)
		thread.start()
		# Setup Notification Queue 
		self.__setupNotificationQueue()
	
	def __createListener(self):
		self.listener = Listener(account=self.pushBulletManager, on_push=self.on_push, http_proxy_host=HTTP_PROXY_HOST, http_proxy_port=HTTP_PROXY_PORT)
		self.listener.run_forever()

	def __setupNotificationQueue(self):
		print("setupNotificationQueue")
		self.notificationQueue = Queue(maxsize=QUEUE_MAX_SIZE)
		for i in range(NUM_THREAD):
			worker = Thread(target=self.__motionNotify, args=())
			worker.setDaemon(True)
			worker.start()

	def pushNotificationToMobile(self, filePath):
		self.notificationQueue.put(filePath)
	
	def pushToMobile(self, dataDictionary):
		print("pushToMobile: ", dataDictionary)
		self.notificationQueue.put(dataDictionary)
	
	def __motionNotify(self):
		print("__motionNotify called")
		while True:
			dataDictionary=self.notificationQueue.get()
			print("upload and notify: ", dataDictionary)
			if dataDictionary['type'] == "TEXT_MESSAGE":
				push = self.pushBulletManager.push_note(dataDictionary['text'],'' )
				print("push result: ", push)
			elif dataDictionary['type'] == "IMAGE_MESSAGE":
				filePath = dataDictionary['filePath']
				print("upload and push file: ", filePath)
				with open(filePath, "rb") as pic:
					fileData = self.pushBulletManager.upload_file(pic, dataDictionary['fileName'])
					push = self.pushBulletManager.push_file(**fileData)
					print("push result: ", push)
					if "iden" in push:
						os.remove(filePath)
			elif dataDictionary['type'] == "VIDEO_MESSAGE":
				push = self.pushBulletManager.push_note("The motion is out. Video uploading...",'')
				filePath = dataDictionary['filePath']
				print("upload and push file: ", filePath)
				with open(filePath, "rb") as pic:
					fileData = self.pushBulletManager.upload_file(pic, dataDictionary['fileName'])
					push = self.pushBulletManager.push_file(**fileData)
					print("push result: ", push)
					if "iden" in push:
						os.remove(filePath)
			else:
				print("Not support type: ", dataDictionary['Type'])		
			self.notificationQueue.task_done()

	def __delete(self):
		self.listener.close() # to stop the run_forever()

	def on_push(self, jsonMessage):
		if jsonMessage["type"] == "tickle" and jsonMessage["subtype"] == "push":
			allPushes = self.pushBulletManager.get_pushes()
			latest = allPushes[0]
			if 'body' in latest:
				body = latest['body']
				print(body)
				if body.startswith("@"):
					self.didReceiveCommand(body)
		#		else:
		#			print("latest pushes: ", latest)	
		#	else:
		#		print("latest pushes: ", latest)	

	def notifyWithImage(self,filePath):
		with open(filePath, "rb") as pic:
			file_data = self.pushBulletManager.upload_file(pic, "picture.jpg")
			push = self.pushBulletManager.push_file(**file_data)
	
	def notifyWithVideo(self,filePath):
		with open(filePath, "rb") as pic:
			file_data = self.pushBulletManager.upload_file(pic, "video.h264")
			push = self.pushBulletManager.push_file(**file_data)
	

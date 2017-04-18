#!/usr/bin/env python
from pushbullet import Listener
from pushbullet import Pushbullet

HTTP_PROXY_HOST = None
HTTP_PROXY_PORT = None

class NotificationHandler:
	def __init__(self, pushBulletAPIKey,didReceiveCommand):
		self.pushBulletAPIKey = pushBulletAPIKey
		self.didReceiveCommand = didReceiveCommand
		self.pushBulletManager = Pushbullet(self.pushBulletAPIKey)
		self.listener = Listener(account=self.pushBulletManager, on_push=self.on_push, http_proxy_host=HTTP_PROXY_HOST, http_proxy_port=HTTP_PROXY_PORT)
		self.listener.run_forever()

	def __delete(self):
		self.listener.close() # to stop the run_forever()

	def on_push(self, jsonMessage):
		print('Received jsonMessage:\n{}'.format(jsonMessage))
		print(jsonMessage.values())
		if jsonMessage["type"] == "tickle" and jsonMessage["subtype"] == "push":
			allPushes = pb.get_pushes()
			latest = allPushes[0]
			body = latest['body']
			print(body)
			self.didReceiveCommand(body)

	def notifyWithImage(self,filePath):
		with open(filePath, "rb") as pic:
			file_data = pb.upload_file(pic, "picture.jpg")
			push = self.pushBulletManager.push_file(**file_data)
	
	def notifyWithVideo(self,filePath):
		with open(filePath, "rb") as pic:
			file_data = pb.upload_file(pic, "video.h264")
			push = self.pushBulletManager.push_file(**file_data)
	

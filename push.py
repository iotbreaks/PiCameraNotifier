#!/usr/bin/env python
from pushbullet import Listener
from pushbullet import Pushbullet

API_KEY = 'o.zfBzBeuIf5A5msLDfUK9mlvtwPK8HG0T'	# YOUR API KEY
HTTP_PROXY_HOST = None
HTTP_PROXY_PORT = None

pb = Pushbullet(API_KEY)

def on_push(data):
	print('Received data:\n{}'.format(data))
	print(data.values())
	if data["type"] == "tickle" and data["subtype"] == "push":
		allPushes = pb.get_pushes()
		latest = allPushes[0]
		print(latest)

def main():
		global pb
		push = pb.push_note("This is the title", "This is the body")
		s = Listener(account=pb,
								 on_push=on_push,
								 http_proxy_host=HTTP_PROXY_HOST,
								 http_proxy_port=HTTP_PROXY_PORT)
		try:
				s.run_forever()
		except KeyboardInterrupt:
				s.close()

if __name__ == '__main__':
		main()


class NotificationHandler:
	def __init__(self, pushBulletAPIKey,didReceiveCommand)
		self.pushBulletAPIKey = pushBulletAPIKey
		self.didReceiveCommand = didReceiveCommand
		self.pushBulletManager = Pushbullet(self.pushBulletAPIKey)
		self.listener = Listener(account=self.pushBulletManager, on_push=self.on_push, http_proxy_host=HTTP_PROXY_HOST, http_proxy_port=HTTP_PROXY_PORT)

	def on_push(self, jsonMessage):
		print('Received jsonMessage:\n{}'.format(jsonMessage))
		print(jsonMessage.values())
		if jsonMessage["type"] == "tickle" and jsonMessage["subtype"] == "push":
			allPushes = pb.get_pushes()
			latest = allPushes[0]
			print(latest)

	def notifyWithImage(self,filePath)
		with open(filePath, "rb") as pic:
			file_data = pb.upload_file(pic, "picture.jpg")
			push = self.pushBulletManager.push_file(**file_data)
	
	def notifyWithVideo(self,filePath)
		with open(filePath, "rb") as pic:
			file_data = pb.upload_file(pic, "video.h264")
			push = self.pushBulletManager.push_file(**file_data)


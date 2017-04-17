#!/usr/bin/env python

__author__ = 'Igor Maculan <n3wtron@gmail.com>'
import logging

from pushbullet import Listener
from pushbullet import Pushbullet
import time
import json
import os
import requests
import subprocess
import websocket

logging.basicConfig(level=logging.DEBUG)

API_KEY = 'o.zfBzBeuIf5A5msLDfUK9mlvtwPK8HG0T'  # YOUR API KEY
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

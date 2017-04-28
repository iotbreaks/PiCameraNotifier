#!/usr/bin/python
import subprocess
import io

WORKING_DIR="/home/pi/Desktop/PiCameraNotifier/"
#process = subprocess.Popen(["ffmpeg", '-framerate', '24', '-i', './video2.h264', '-c', 'copy', 'output.mp4'], stdout=subprocess.PIPE)
process = subprocess.Popen(["ls", '-l'])
out, err = process.communicate()
print(out)
with io.open(WORKING_DIR+'test.log', 'wb') as output:
	output.write("This is something fucking cool")

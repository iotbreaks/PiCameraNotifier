#!/usr/bin/python
import subprocess
import io

WORKING_DIR="/home/pi/Desktop/Kenny/PiCameraNotifier/"
process = subprocess.Popen([ WORKING_DIR + '/systemInfo.sh'], stdout=subprocess.PIPE)
out, err = process.communicate()
print(out)
with io.open(WORKING_DIR+'test.log', 'wb') as output:
	output.write(out)

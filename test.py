#!/usr/bin/python
import subprocess
process = subprocess.Popen(['./systemInfo.sh'], stdout=subprocess.PIPE)
out, err = process.communicate()
print(out)

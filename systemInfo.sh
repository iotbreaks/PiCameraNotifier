#!/bin/bash
temperature=`/opt/vc/bin/vcgencmd measure_temp`
RAM=`free -h  | grep "Mem" | awk '{print "RAM(Free/Total):", $4,"/",$2}'`
usedCPU=`top -n 1 | head -n 8 | tail -n 1| awk '{print "CPU used: ",$10, "%"}'`
SDCard=`df -Bh | awk  '/root/ {print "SDCard(Free/Total): ", $4,"/",$2}'`
echo $temperature". "$RAM". "$usedCPU". "$SDCard

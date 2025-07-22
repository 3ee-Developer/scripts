#!/bin/bash

# workaround: Check last run 
DATE=$(date +"%Y%m%d")
LASTRUN_FILE=/root/log/fromLambdaLastRun.log
LOG=/root/log/fromLambda.log
LASTRUN=$(cat $LASTRUN_FILE)
if [ "$DATE" == "$LASTRUN" ]; then
	echo "Ya corrio! $(date)" >> $LOG
  ##nohup /root/scripts/apagarServerTasks.sh >> /root/log/apagarServerTasks.log 2>&1 &
	exit 0
fi
echo $DATE > $LASTRUN_FILE
echo $(date) >> $LOG

nohup time /root/scripts/backoffice.sh >> /root/log/backoffice.log 2>&1 &
nohup time /root/scripts/uniswap2.sh >> /root/log/uniswap2.log 2>&1 &
nohup time /root/scripts/hyperliquid.sh >> /root/log/hyperliquid.log 2>&1 &
nohup time /root/scripts/hyperliquid_test.sh >> /root/log/hyperliquid_test.log 2>&1 &
nohup /root/scripts/apagarServerTasks.sh >> /root/log/apagarServerTasks.log 2>&1 &
#python3 /root/test.py >> /root/test.log

#!/bin/bash

# workaround: Check last run 
DATE=$(date +"%Y%m%d")
LASTRUN_FILE=/root/log/fromLambdaLastRun.log
LOG=/root/log/fromLambda.log
LASTRUN=$(cat $LASTRUN_FILE)
if [ "$DATE" == "$LASTRUN" ]; then
	echo "Ya corrio! $(date)" >> $LOG
  nohup /root/scripts/apagarServerUniswap.sh >> /root/log/apagarServerUniswap.log 2>&1 &
	exit 0
fi
echo $DATE > $LASTRUN_FILE
echo $(date) >> $LOG

# Mantener el orden ya que apagan el servidor
nohup time /root/scripts/uniswap.sh >> /root/log/uniswap.log 2>&1 &
nohup /root/scripts/apagarServerUniswap.sh >> /root/log/apagarServerUniswap.log 2>&1 &
#python3 /root/test.py >> /root/test.log

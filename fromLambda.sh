#!/bin/bash

# workaround: Check last run 
DATE=$(date +"%Y%m%d")
LASTRUN_FILE=/root/log/fromLambdaLastRun.log
LOG=/root/log/fromLambda.log
LASTRUN=$(cat $LASTRUN_FILE)
if [ "$DATE" == "$LASTRUN" ]; then
	echo "Ya corrio! $(date)" >> $LOG
	exit 0
fi
echo $DATE > $LASTRUN_FILE
echo $(date) >> $LOG

# Mantener el orden ya que apagan el servidor
nohup time /root/scripts/backoffice.sh >> /root/log/backoffice.log 2>&1 & 
nohup time /root/scripts/uniswap.sh >> /root/log/uniswap.log 2>&1 &
nohup time /root/scripts/uniswap2.sh >> /root/log/uniswap2.log 2>&1 &
nohup time /root/scripts/hyperliquid.sh >> /root/log/hyperliquid.log 2>&1 &
nohup time /root/scripts/hyperliquid_evolution.sh >> /root/log/hyperliquid_evolution.log 2>&1 &
nohup time /root/scripts/hyperliquid_test.sh >> /root/log/hyperliquid_test.log 2>&1 &
nohup sleep 600 && /root/scripts/apagarServer.sh >> /root/log/apagarServer.log 2>&1 &
#python3 /root/test.py >> /root/test.log

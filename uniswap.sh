#!/bin/bash

LOG=/root/log/uniswap.log

echo "--------------------------------------------------------------------------" | tee -a $LOG
echo $(date) | tee -a $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python3 uni_main.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


#!/bin/bash

LOG=/root/log/hyperliquid.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python3 valuation_hyperliquid.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

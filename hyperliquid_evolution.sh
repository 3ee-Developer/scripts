#!/bin/bash

LOG=/root/log/hyperliquid_evolution.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python3 valuation_hyperliquid_evolution.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

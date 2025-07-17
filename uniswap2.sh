#!/bin/bash

LOG=/root/log/uniswap2.log

echo "--------------------------------------------------------------------------" | tee -a $LOG
echo $(date) | tee -a $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python3 valuation_uniswap.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


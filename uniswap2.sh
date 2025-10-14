#!/bin/bash

LOG=/root/log/uniswap2.log

echo "--------------------------------------------------------------------------" | tee -a $LOG
echo $(date) | tee -a $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv2/bin/activate >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py uniswap2 >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


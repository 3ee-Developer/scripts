#!/bin/bash

LOG=/root/log/shield.log

echo "--------------------------------------------------------------------------" | tee -a $LOG
echo $(date) | tee -a $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv2/bin/activate >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py damm >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


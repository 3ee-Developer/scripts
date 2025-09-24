#!/bin/bash

LOG=/root/log/hyperliquid_evolution.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py hyperliquid2 >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

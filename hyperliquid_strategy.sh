#!/bin/bash

LOG=/root/log/hyperliquid.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib && source venv2/bin/activate
cd /root/defilib_coded_strats >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py --no-valuate hyperliquid >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

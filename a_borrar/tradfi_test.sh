#!/bin/bash

LOG=/root/log/tradfi_fund_test.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv2/bin/activate >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py --no-strategy tradfi_fund_test >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

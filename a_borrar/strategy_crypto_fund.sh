#!/bin/bash

LOG=/root/log/strategy_crypto_fund.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib >> $LOG 2>&1  && \
	source venv2/bin/activate >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py strategy_crypto_fund >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

#!/bin/bash

LOG=/root/log/3ee_systematic_vault.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib && source venv2/bin/activate
cd /root/defilib_3ee_vault >> $LOG 2>&1  && \
	python3 scripts/backoffice/valuate-and-run.py --no-valuate 3ee_systematic_vault >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

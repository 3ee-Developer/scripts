#!/bin/bash

LOG=/root/log/3ee_systematic_vault.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/defilib && source venv2/bin/activate
cd /root/defilib_3ee_vault >> $LOG 2>&1  && \
	python3 hlq_vault.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1

#!/bin/bash

LOG=/root/log/backoffice.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

cd /root/backoffice >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python aws_run.py >> $LOG 2>&1  && \
	python upload_gsheets_data.py --aws >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


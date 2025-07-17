#!/bin/bash

LOG=/root/log/backoffice.log

echo "--------------------------------------------------------------------------" >> $LOG
echo $(date) >> $LOG

# Clean docker images 
#docker rm $(docker ps -a -q)
#docker rmi $(docker images -a -q)

# Auth
##aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 116981762920.dkr.ecr.us-east-2.amazonaws.com

# Exec
##docker pull 116981762920.dkr.ecr.us-east-2.amazonaws.com/3ee/backend_gsheets:latest
##docker tag 116981762920.dkr.ecr.us-east-2.amazonaws.com/3ee/backend_gsheets 3ee/backend_gsheets
##docker run 3ee/backend_gsheets


cd /root/backoffice >> $LOG 2>&1  && \
	source venv/bin/activate >> $LOG 2>&1  && \
	python aws_run.py >> $LOG 2>&1  && \
	deactivate >> $LOG 2>&1


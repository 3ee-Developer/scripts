#!/bin/bash

IFS=' '
PROCESS="aws_run.py valuate-and-run"

function shutdownTasks() {
	for proc in $PROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(tasks) $proc corriendo"
			sleep 30
			shutdownTasks
		fi
	done
	# 3ee_tasks
	echo "--- $(date) Apagando 3ee_tasks ---"
	ps awx
	aws ec2 stop-instances --instance-ids i-086cd22c6d66f5cab

}

echo $(date)
sleep 900
shutdownTasks

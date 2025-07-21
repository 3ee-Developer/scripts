#!/bin/bash

IFS=' '
PROCESS="aws_run.py valuation_uniswap.py valuation_hyperliquid.py valuation_hyperliquid_test.py"

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
	echo "--- Apagando 3ee_tasks ---"
	ps awx
	aws ec2 stop-instances --instance-ids i-086cd22c6d66f5cab

}

echo $(date)
shutdownTasks

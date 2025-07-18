#!/bin/bash

IFS=' '
PROCESS="uni_main.py"

function shutdownUniswap() {
	for proc in $PROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(task) $proc corriendo"
			sleep 30
			shutdownTask
		fi
	done
	# 3ee_tasks
	echo "--- Apagando 3ee_tasks ---"
	ps awx
	#shutdown -h now
	aws ec2 stop-instances --instance-ids i-042ec3e7fa3906e4b

}

echo $(date)
shutdownUniswap

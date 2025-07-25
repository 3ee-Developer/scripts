#!/bin/bash

IFS=' '
PROCESS="uni_main.py"

function shutdownUniswap() {
	for proc in $PROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(uniswap) $proc corriendo"
			sleep 30
			shutdownUniswap
		fi
	done
	echo "--- $(date) Apagando 3ee_uniswap ---"
	ps awx
	aws ec2 stop-instances --instance-ids i-042ec3e7fa3906e4b

}

echo $(date)
sleep 60
shutdownUniswap

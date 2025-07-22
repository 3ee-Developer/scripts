#!/bin/bash

IFS=' '
PROCESS="valuation_hyperliquid_evolution.py"

function shutdownHyperliquid() {
	for proc in $PROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(task) $proc corriendo"
			sleep 30
			shutdownHyperliquid
		fi
	done
	echo "--- Apagando 3ee_hyperliquid ---"
	ps awx
	##aws ec2 stop-instances --instance-ids i-09a4ecb38ca786bc5
}

echo $(date)
shutdownHyperliquid

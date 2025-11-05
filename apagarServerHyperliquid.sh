#!/bin/bash

IFS=' '
PROCESS="valuate-and-run"

function shutdownHyperliquid() {
	cd /root/scripts && source venv/bin/activate && python3 monitor.py && deactivate && cd -
	for proc in $PROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(hyperliquid) $proc corriendo"
			sleep 30
			shutdownHyperliquid
		fi
	done
	echo "--- $(date) Apagando 3ee_hyperliquid ---"
	ps awx
	aws ec2 stop-instances --instance-ids i-09a4ecb38ca786bc5
}

echo $(date)
# 15 minutos
sleep 900
shutdownHyperliquid

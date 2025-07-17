#!/bin/bash

IFS=' '
PROCESS="aws_run.py uni_main.py valuation_uniswap.py valuation_hyperliquid.py valuation_hyperliquid_evolution.py valuation_hyperliquid_test.py"
CoSignerPROCESS="uni_main.py valuation_uniswap.py"

function shutdownTask() {
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
	aws ec2 stop-instances --instance-ids i-086cd22c6d66f5cab

}

function shutdownCoSigner() {
	for proc in $CoSignerPROCESS; do
		check=$(ps awx | grep "$proc" | grep -v grep)
		if [ "$check" != "" ]; then
			echo "(cosigner) $proc corriendo"
			sleep 30
			shutdownCoSigner
		fi
	done
	# Co-Signer
	echo "--- Apagando cosigner ---"
	aws ec2 stop-instances --instance-ids i-01993d9e57b195144 
}

function shutdown() {
	shutdownCoSigner
	shutdownTask
}
echo $(date)
shutdown

#!/bin/bash

# Función común para apagar servidores
# Parámetros:
#   $1: Lista de procesos a monitorear (separados por espacios)
#   $2: ID de la instancia EC2 a apagar
#   $3: Nombre del servidor (opcional, para mensajes)

function shutdownServer() {
	local PROCESS="$1"
	local INSTANCE_ID="$2"
	local SERVER_NAME="${3:-server}"
	
	IFS=' '

	# Monitor
	echo "Monitoring server..."
	cd /root/scripts && source venv/bin/activate && python3 monitor.py && deactivate && cd -
	
	# Monitor processes
	echo "Monitoring processes..."
	while true; do
		all_done=true
		for proc in $PROCESS; do
			check=$(ps awx | grep "$proc" | grep -v grep)
			if [ "$check" != "" ]; then
				all_done=false
				break
			fi
		done
		if [ "$all_done" = true ]; then
			# Todos los procesos terminaron
			break
		fi
		sleep 60

		# Monitor
		echo "Monitoring server..."
		cd /root/scripts && source venv/bin/activate && python3 monitor.py && deactivate && cd -
	done
	
	# Upload gsheet
	cd /root/defilib && source venv2/bin/activate
	while true; do
		echo "Uploading gsheet..."
		python3 scripts/backoffice/upload_gsheet.py
		if [ $? -eq 0 ]; then
			echo "Upload gsheet success"
			break
		fi
		echo "Upload gsheet failed"
		sleep 10
	done
	
	# Shutdown
	echo "--- $(date) Apagando $SERVER_NAME ---"
	ps awx
	aws ec2 stop-instances --instance-ids $INSTANCE_ID
}


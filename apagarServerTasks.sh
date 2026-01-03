#!/bin/bash

# Cargar función común de shutdown
source "$(dirname "$0")/shutdown_common.sh"

PROCESS="aws_run.py valuate-and-run"
INSTANCE_ID="i-086cd22c6d66f5cab"
SERVER_NAME="3ee_tasks"

# IDs de las instancias que deben estar detenidas antes de apagar
CHECK_UNISWAP_SERVER="i-042ec3e7fa3906e4b"
CHECK_HYPERLIQUID_SERVER="i-09a4ecb38ca786bc5"

# ID de API Cosigner
API_COSIGNER_SERVER="i-01993d9e57b195144"

# Función para verificar el estado de una instancia
check_instance_state() {
    local instance_id=$1
    aws ec2 describe-instances --instance-ids "$instance_id" \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text 2>/dev/null
}

# Esperar hasta que ambas instancias estén en estado "stopped"
echo "$(date) - Esperando que las instancias $CHECK_UNISWAP_SERVER y $CHECK_HYPERLIQUID_SERVER estén detenidas..."
while true; do
    state1=$(check_instance_state "$CHECK_UNISWAP_SERVER")
    state2=$(check_instance_state "$CHECK_HYPERLIQUID_SERVER")
    
    echo "$(date) - Estado de $CHECK_UNISWAP_SERVER: $state1"
    echo "$(date) - Estado de $CHECK_HYPERLIQUID_SERVER: $state2"
    
    if [ "$state1" = "stopped" ] && [ "$state2" = "stopped" ]; then
        echo "$(date) - Ambas instancias están detenidas. Procediendo a apagar el servidor..."
        break
    fi
    
    echo "$(date) - Esperando 30 segundos antes de verificar nuevamente..."
    sleep 30
done

# Apagar API_COSIGNER_SERVER sin verificar procesos
echo "$(date) - Apagando API_COSIGNER_SERVER ($API_COSIGNER_SERVER) sin verificar procesos..."
aws ec2 stop-instances --instance-ids "$API_COSIGNER_SERVER"

echo $(date)
shutdownServer "$PROCESS" "$INSTANCE_ID" "$SERVER_NAME"

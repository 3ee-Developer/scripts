#!/bin/bash

# Cargar función común de shutdown
source "$(dirname "$0")/shutdown_common.sh"

PROCESS="uni_main.py"
INSTANCE_ID="i-042ec3e7fa3906e4b"
SERVER_NAME="3ee_uniswap"

echo $(date)
shutdownServer "$PROCESS" "$INSTANCE_ID" "$SERVER_NAME"

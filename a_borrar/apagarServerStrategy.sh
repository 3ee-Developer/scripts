#!/bin/bash

# Cargar función común de shutdown
source "$(dirname "$0")/shutdown_common.sh"

PROCESS="valuate-and-run"
INSTANCE_ID="i-09a4ecb38ca786bc5"
SERVER_NAME="3ee_strategy"

echo $(date)
shutdownServer "$PROCESS" "$INSTANCE_ID" "$SERVER_NAME"

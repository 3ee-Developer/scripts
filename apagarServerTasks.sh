#!/bin/bash

# Cargar función común de shutdown
source "$(dirname "$0")/shutdown_common.sh"

PROCESS="aws_run.py valuate-and-run"
INSTANCE_ID="i-086cd22c6d66f5cab"
SERVER_NAME="3ee_tasks"

echo $(date)
sleep 900
shutdownServer "$PROCESS" "$INSTANCE_ID" "$SERVER_NAME"

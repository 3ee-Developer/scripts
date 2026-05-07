#!/bin/bash

# Cargar función común de shutdown
source "$(dirname "$0")/shutdown_common.sh"

PROCESS="aws_run.py valuate-and-run"
INSTANCE_ID="-"
SERVER_NAME=$1

echo $(date)
shutdownServer "$PROCESS" "$INSTANCE_ID" "$SERVER_NAME"

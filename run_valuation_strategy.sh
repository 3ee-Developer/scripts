#!/bin/bash

set -euo pipefail

LOG=""
NO_VALUATE=0
NO_STRATEGY=0
FUND=""

usage() {
  echo "Usage: $0 <fund_name> [--no-valuate] [--no-strategy]" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-valuate)
      NO_VALUATE=1
      shift
      ;;
    --no-strategy)
      NO_STRATEGY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -n "$FUND" ]]; then
        echo "Unexpected extra argument: $1" >&2
        usage
        exit 2
      fi
      FUND="$1"
      shift
      ;;
  esac
done

if [[ -z "$FUND" ]]; then
  usage
  exit 2
fi

if [[ "$NO_VALUATE" -eq 1 ]]; then
  LOG="/root/log/fund_strategy.log"
elif [[ "$NO_STRATEGY" -eq 1 ]]; then
  LOG="/root/log/fund_valuation.log"
else
  LOG="/root/log/${FUND}.log"
fi

echo "--------------------------------------------------------------------------" >> "$LOG"
echo "$(date) -- fund=$FUND" >> "$LOG"

if [[ "$NO_VALUATE" -eq 1 && "$NO_STRATEGY" -eq 1 ]]; then
  echo "Nothing to do: --no-valuate and --no-strategy both set" >> "$LOG"
  exit 0
fi

PY_ARGS=()
if [[ "$NO_VALUATE" -eq 1 ]]; then PY_ARGS+=(--no-valuate); fi
if [[ "$NO_STRATEGY" -eq 1 ]]; then PY_ARGS+=(--no-strategy); fi

cd /root/defilib
source venv2/bin/activate
python3 scripts/backoffice/valuate-and-run.py "$FUND" "${PY_ARGS[@]}" >> "$LOG" 2>&1
python3 scripts/backoffice/upload_gsheet.py --fund "$FUND" "${PY_ARGS[@]}" >> "$LOG" 2>&1
deactivate >> "$LOG" 2>&1

#!/usr/bin/env bash
# fuzz_perf.sh - load generator for the options pricer
# Usage:
#   ./fuzz_perf.sh [total] [concurrency] [host]
# Example:
#   ./fuzz_perf.sh 20000 200 http://localhost:8080/price

set -euo pipefail
IFS=$'\n\t'

TOTAL="${1:-10000}"
CONCURRENCY="${2:-100}"
HOST="${3:-http://localhost:8080/price}"

LAT_FILE=$(mktemp /tmp/lat.XXXXXX)
ERR_FILE=$(mktemp /tmp/err.XXXXXX)

echo "Load test: total=$TOTAL, concurrency=$CONCURRENCY, host=$HOST"
echo "Metrics -> $LAT_FILE / $ERR_FILE"
echo

generate_params() {
  local spot strike rate vol expiry
  spot=$(awk -v min=80 -v max=120 'BEGIN{srand(); print min+rand()*(max-min)}')
  strike=$(awk -v min=80 -v max=120 'BEGIN{srand(); print min+rand()*(max-min)}')
  rate=$(awk -v min=0.0 -v max=0.05 'BEGIN{srand(); print min+rand()*(max-min)}')
  vol=$(awk -v min=0.1 -v max=0.5 'BEGIN{srand(); print min+rand()*(max-min)}')
  expiry=$(awk -v min=0.01 -v max=2.0 'BEGIN{srand(); print min+rand()*(max-min)}')
  printf "spot=%.2f&strike=%.2f&rate=%.4f&vol=%.3f&expiry=%.3f" "$spot" "$strike" "$rate" "$vol" "$expiry"
}

worker() {
  local ts_start ts_end lat code
  local params
  params=$(generate_params)
  # small random delay to avoid bursts
  usleep $((RANDOM % 5000)) 2>/dev/null || sleep 0.$((RANDOM % 5))
  ts_start=$(date +%s.%N)
  code=$(curl -s -o /dev/null -w "%{http_code}" "$HOST?$params" || echo "000")
  ts_end=$(date +%s.%N)
  lat=$(awk -v a="$ts_start" -v b="$ts_end" 'BEGIN{printf "%.6f", b - a}')
  echo "$lat" >>"$LAT_FILE"
  if [ "$code" != "200" ]; then
    echo "HTTP:$code PARAMS:$params" >>"$ERR_FILE"
  fi
}

export -f generate_params worker
export LAT_FILE ERR_FILE HOST

seq 1 "$TOTAL" | xargs -n1 -P"$CONCURRENCY" -I{} bash -c 'worker' 2>/dev/null

TOTAL_REQ=$(wc -l < "$LAT_FILE")
ERROR_REQ=$(wc -l < "$ERR_FILE" || echo 0)
SUCCESS_REQ=$((TOTAL_REQ - ERROR_REQ))
MIN_LAT=$(sort -n "$LAT_FILE" | head -1)
MAX_LAT=$(sort -n "$LAT_FILE" | tail -1)
AVG_LAT=$(awk '{sum+=$1} END {if (NR>0) printf "%.6f", sum/NR; else print "0"}' "$LAT_FILE")
P95_LAT=$(awk ' {a[NR]=$1} END{ if(NR==0){print 0; exit} asort(a); idx=int(0.95*NR+0.5); if(idx<1) idx=1; if(idx>NR) idx=NR; print a[idx] }' "$LAT_FILE")

echo
echo "Requests: total=$TOTAL_REQ, success=$SUCCESS_REQ, errors=$ERROR_REQ"
echo "Latency (s): min=$MIN_LAT avg=$AVG_LAT p95=$P95_LAT max=$MAX_LAT"
echo
echo "Latency file: $LAT_FILE"
echo "Error file:   $ERR_FILE"


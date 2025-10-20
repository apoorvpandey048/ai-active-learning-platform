#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "Stopping any running backend instances..."
# Kill any running python process running backend/app.py
pkill -f "backend/app.py" || true
sleep 0.5

LOG=backend/backend.log
echo "Starting backend and redirecting logs to $LOG"
# Start the Flask app in background; use nohup so it survives the shell exit.
nohup python3 backend/app.py > "$LOG" 2>&1 &
PID=$!
echo "Backend PID: $PID"

echo "Waiting for server to start (polling /health up to 20s)..."
RETRIES=20
SLEEP=1
UP=false
for i in $(seq 1 $RETRIES); do
	if curl -sS http://localhost:5000/health >/dev/null 2>&1; then
		echo "Server is up (after ${i}s)"
		UP=true
		break
	fi
	sleep $SLEEP
done

if [ "$UP" != "true" ]; then
	echo "Server did not start within $((RETRIES*SLEEP))s. Showing backend log tail:"
	tail -n 200 "$LOG" || true
	echo "Exiting with failure."
	exit 1
fi

echo "Running smoke test runner..."
python3 backend/smoke_test_runner.py || true

echo "Tailing last 50 lines of backend log ($LOG):"
tail -n 50 "$LOG" || true

echo "Done. If tests failed, inspect $LOG for details."

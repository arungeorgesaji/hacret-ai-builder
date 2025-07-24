#!/bin/bash

cleanup() {
    echo -e "\nCleaning up FastAPI server..."
    if [ ! -z "$UVICORN_PID" ]; then
        echo "Stopping FastAPI server (PID: $UVICORN_PID)"
        kill $UVICORN_PID 2>/dev/null
        wait $UVICORN_PID 2>/dev/null
    fi
    pkill -f "uvicorn main:app" 2>/dev/null
    echo "FastAPI cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

AVAILABLE_PORT=$(
  for port in {5000..9000}; do
    (echo >/dev/tcp/localhost/$port) 2>/dev/null || { echo $port; break; }
  done
)

echo "Starting FastAPI server on port $AVAILABLE_PORT..."
python -m uvicorn main:app --host 0.0.0.0 --port $AVAILABLE_PORT --reload &
UVICORN_PID=$!

echo "FastAPI server started with PID: $UVICORN_PID"

if ! kill -0 $UVICORN_PID 2>/dev/null; then
    echo "Error: FastAPI server failed to start"
    exit 1
fi

echo "FastAPI server running on localhost:$AVAILABLE_PORT"
echo "Press Ctrl+C to stop the server"

while true; do
    if ! kill -0 $UVICORN_PID 2>/dev/null; then
        echo "FastAPI server stopped unexpectedly"
        break
    fi
    sleep 5
done

cleanup

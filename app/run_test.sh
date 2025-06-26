#!/bin/bash

cleanup() {
    echo -e "\nCleaning up..."
    if [ ! -z "$UVICORN_PID" ]; then
        echo "Stopping FastAPI server (PID: $UVICORN_PID)"
        kill $UVICORN_PID 2>/dev/null
        wait $UVICORN_PID 2>/dev/null
    fi
    if [ ! -z "$NGROK_PID" ]; then
        echo "Stopping ngrok (PID: $NGROK_PID)"
        kill $NGROK_PID 2>/dev/null
        wait $NGROK_PID 2>/dev/null
    fi
    pkill -f "uvicorn main:app" 2>/dev/null
    pkill -f "ngrok http" 2>/dev/null
    echo "Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

AVAILABLE_PORT=$(
  for port in {5000..9000}; do
    (echo >/dev/tcp/localhost/$port) 2>/dev/null || { echo $port; break; }
  done
)

echo "Starting FastAPI server..."
python -m uvicorn main:app --host 0.0.0.0 --port $AVAILABLE_PORT --reload &
UVICORN_PID=$!

echo "FastAPI server started with PID: $UVICORN_PID"

if ! kill -0 $UVICORN_PID 2>/dev/null; then
    echo "Error: FastAPI server failed to start"
    exit 1
fi

echo "Starting ngrok tunnel..."
$HOME/ngrok http --url=admittedly-wired-halibut.ngrok-free.app $AVAILABLE_PORT &
NGROK_PID=$!

echo "ngrok started with PID: $NGROK_PID"

if ! kill -0 $NGROK_PID 2>/dev/null; then
    echo "Error: ngrok failed to start"
    exit 1
fi

echo "ngrok tunnel active at: https://admittedly-wired-halibut.ngrok-free.app"
echo "FastAPI server running on localhost:$AVAILABLE_PORT"
echo "Press Ctrl+C to stop both services"

while true; do
    if ! kill -0 $UVICORN_PID 2>/dev/null; then
        echo "FastAPI server stopped unexpectedly"
        break
    fi
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        echo "ngrok stopped unexpectedly"
        break
    fi
    sleep 5
done

cleanup

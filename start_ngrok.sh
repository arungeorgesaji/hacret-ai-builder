#!/bin/bash

cleanup() {
    echo -e "\nCleaning up ngrok..."
    if [ ! -z "$NGROK_PID" ]; then
        echo "Stopping ngrok (PID: $NGROK_PID)"
        kill $NGROK_PID 2>/dev/null
        wait $NGROK_PID 2>/dev/null
    fi
    pkill -f "ngrok http" 2>/dev/null
    echo "ngrok cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

if [ -z "$1" ]; then
    echo "Error: Please specify the port FastAPI is running on"
    echo "Usage: $0 <port>"
    exit 1
fi

FASTAPI_PORT=$1

echo "Starting ngrok tunnel for FastAPI on port $FASTAPI_PORT..."

if [ -f "$HOME/ngrok" ]; then
    $HOME/ngrok http --url=admittedly-wired-halibut.ngrok-free.app $FASTAPI_PORT &
else
    ngrok http --url=admittedly-wired-halibut.ngrok-free.app $FASTAPI_PORT &
fi

NGROK_PID=$!

echo "ngrok started with PID: $NGROK_PID"

if ! kill -0 $NGROK_PID 2>/dev/null; then
    echo "Error: ngrok failed to start"
    exit 1
fi

echo "ngrok tunnel active at: https://admittedly-wired-halibut.ngrok-free.app"
echo "Press Ctrl+C to stop ngrok"

while true; do
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        echo "ngrok stopped unexpectedly"
        break
    fi
    sleep 5
done

cleanup

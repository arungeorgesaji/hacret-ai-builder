#Find available ports in nest
AVAILABLE_PORT=$(
  for port in {5000..9000}; do
    (echo >/dev/tcp/localhost/$port) 2>/dev/null || { echo $port; break; }
  done
)

#Create Tunnel using ngrok(I use nest so just installed binary)
$HOME/ngrok http --url=admittedly-wired-halibut.ngrok-free.app $AVAILABLE_PORT 

#Run FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port $AVAILABLE_PORT --reload

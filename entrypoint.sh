#!/bin/bash
# Start the Tor service in the background
echo "[*] Booting Tor Overmind..."
service tor start

# Wait for Tor circuit to establish
sleep 10
echo "[*] Tor Circuit Established. Igniting SovereignCore..."

# Launch the three cores concurrently
python prophet_pipeline.py &
python swarm_api.py &
python divination_core.py

# Keep container alive
wait -n

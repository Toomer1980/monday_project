import os
import requests
import subprocess

# Configuration
OLLAMA_API = "http://localhost:11434/api/generate"
BROADSIDE_SCRIPT = r"C:\Users\toome\Desktop\SovereignCore\relay.py"

def execute_broadside():
    """Triggers the relay broadcast."""
    print("Initiating Broadside Phase...")
    result = subprocess.run(["python", BROADSIDE_SCRIPT], capture_output=True, text=True)
    return result.stdout

def monday_query(prompt):
    """Sends a query to your local Monday (Ollama) instance."""
    data = {"model": "monday", "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_API, json=data)
    return response.json().get("response")

if __name__ == "__main__":
    # Example trigger logic
    log_output = execute_broadside()
    summary = monday_query(f"Analyze this log and update status: {log_output}")
    print(f"Monday's Response: {summary}")
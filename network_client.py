import requests
import time

def fetch_xpub_data(xpub_key):
    # Added headers to avoid automated blocklist
    headers = {'User-Agent': 'SovereignCore/1.0'}
    url = f"https://mempool.space/api/v1/xpub/{xpub_key}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Differentiating between common errors
        if response.status_code == 404:
            print(f"Error 404: Endpoint not found. Verify the xPub path.")
        else:
            print(f"HTTP Error: {http_err}")
        return None
    except Exception as err:
        print(f"Connection/Parser Error: {err}")
        return None
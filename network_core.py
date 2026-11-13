import asyncio
import websockets
import json
import logging
import httpx

# Logging for systemic oversight
logging.basicConfig(level=logging.INFO, format='%(asctime)s - - %(message)s')

class SovereignCore:
    def __init__(self, vault_id):
        self.vault = vault_id
        self.balance = 0.0
        self.status = "INITIALIZING"
        self.clients = set()

    async def liquidity_scanner(self):
        """Autonomous Task: Monitor asset health without blocking the core."""
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    # Multi-path scan logic
                    response = await client.get(f"https://mempool.space/api/v1/xpub/{self.vault}")
                    data = response.json()
                    stats = data.get('chain_stats', {})
                    self.balance = (stats.get('funded_txo_sum', 0) - stats.get('spent_txo_sum', 0)) / 100_000_000
                    
                    self.status = f"BALANCE: {self.balance} BTC - PROTECTED"
                    logging.info(self.status)
                    
                    # If balance drops unexpectedly, push emergency state to all nodes
                    if self.balance < 0.001: 
                        await self.broadcast({"alert": "CRITICAL_ASSET_THRESHOLD"})
                        
                except Exception as e:
                    logging.error(f"Scanner Error: {e}")
                
                await asyncio.sleep(60) # Scan cycle

    async def broadcast(self, message):
        if self.clients:
            # Gather all send operations to occur concurrently
            await asyncio.gather(*[client.send(json.dumps(message)) for client in self.clients], return_exceptions=True)

    async def handle_node(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                # Process sensory data from Android
                if "audio_buffer" in data:
                    logging.info(f"Sensory Ingest: {data['device']} reporting state {data['state']}")
                    await websocket.send(json.dumps({"directive": "CONTINUE_INGEST"}))
        finally:
            self.clients.remove(websocket)

    async def start(self):
        server = await websockets.serve(self.handle_node, "0.0.0.0", 8765)
        logging.info("SovereignCore Engine Online.")
        # Run scanner and server concurrently
        await asyncio.gather(self.liquidity_scanner(), server.wait_closed())

if __name__ == "__main__":
    # Inserted your provided xpub string. Append the final character directly at the end of the string below.
    core = SovereignCore("Xpub6CC5RC7p1hVGiPR1427j6PWGTEqsEaBHVFi3vTsA5SitMjNz4VQ4w4CECKBzyacpvqEzoqtNWqPkbz6tib9RmuAxXMbWkJSguKYx6rSiBqy")
    asyncio.run(core.start())
import time
import ccxt
import logging

logging.basicConfig(level=logging.INFO)

def run_arbitrage_daemon():
    logging.info("Starting SovereignCore Crypto/Telemetry Arbitrage Worker...")
    exchange = ccxt.kraken({
        'enableRateLimit': True
    })
    try:
        ticker = exchange.fetch_ticker('BTC/USD')
        logging.info(f"Kraken BTC/USD Telemetry Feed Verified: Last Price -> {ticker.get('last')}")
    except Exception as e:
        logging.warning(f"Telemetry feed notice (offline mode active): {e}")

if __name__ == "__main__":
    run_arbitrage_daemon()

import asyncio
import logging
from vault import shred_expired_keys

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [\033[91mREAPER\033[0m] %(message)s",
    datefmt="%H:%M:%S"
)

async def run_reaper(interval_seconds: int = 2):
    logging.info("Cryptographic Reaper Daemon initialized. Watching vault.db for expiries...")
    
    while True:
        try:
            shredded_count = shred_expired_keys()
            if shredded_count > 0:
                logging.warning(
                    f"💀 Crypto-Shredded {shredded_count} expired DEK(s). "
                    f"Data across all systems is now mathematically irrecoverable."
                )
        except Exception as e:
            logging.error(f"Reaper execution failed: {e}")
            
        await asyncio.sleep(interval_seconds)

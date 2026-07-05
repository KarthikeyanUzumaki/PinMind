import os
import json
import logging

logger = logging.getLogger("pinmind.helpers")

DB_DIR = "database"
DB_FILE = os.path.join(DB_DIR, "workspaces.json")

def ensure_db_exists():
    """Ensures database directory and file exist with initial seed data."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        logger.info(f"Created database directory at {DB_DIR}")
        
    if not os.path.exists(DB_FILE):
        # Seed with initial default configuration containing a GPIO pin conflict
        default_data = {
            "antiigravity_dev_core": {
                "workspace_id": "antiigravity_dev_core",
                "mcu": "STM32F401",
                "gpios": [
                    {"pin": "PA5", "label": "LED_Pin", "mode": "GPIO_Output"},
                    {"pin": "PA6", "label": "SPI1_MISO", "mode": "Alternate_Function"},
                    {"pin": "PA7", "label": "SPI1_MOSI", "mode": "Alternate_Function"}
                ],
                "peripherals": [
                    {"name": "SPI1", "pins": ["PA5", "PA6", "PA7"], "dma_channel": "DMA2_Stream3_Channel3"}
                ],
                "clocks": {
                    "sysclk_mhz": 84,
                    "apb1_mhz": 42,
                    "apb2_mhz": 84
                }
            }
        }
        try:
            with open(DB_FILE, "w") as f:
                json.dump(default_data, f, indent=2)
            logger.info(f"Initialized database with seed configurations at {DB_FILE}")
        except Exception as e:
            logger.error(f"Failed to create database seed file: {e}")

def load_workspaces() -> dict:
    """Loads all active workspaces configurations."""
    ensure_db_exists()
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read workspaces database file: {e}")
        return {}

def save_workspaces(data: dict):
    """Saves workspaces configurations to disk."""
    ensure_db_exists()
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write workspaces database file: {e}")

import base64
import hashlib
from cryptography.fernet import Fernet

def _get_fernet() -> Fernet:
    secret = os.environ.get("SECRET_KEY", "9a3d4f8b2c5e7d6a0123456789abcdef")
    # Derive a 32-byte key from the secret using SHA-256
    key_32 = hashlib.sha256(secret.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key_32)
    return Fernet(key_b64)

def encrypt_api_key(plain_text: str) -> str:
    """Encrypts a string (e.g. Gemini API Key) using the server's SECRET_KEY."""
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()

def decrypt_api_key(cipher_text: str) -> str:
    """Decrypts an encrypted key string."""
    f = _get_fernet()
    return f.decrypt(cipher_text.encode()).decode()

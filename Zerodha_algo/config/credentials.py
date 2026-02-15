import os
from pathlib import Path
try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None

# Load .env from repo root if python-dotenv is available
ROOT = Path(__file__).resolve().parents[1]
if load_dotenv:
	load_dotenv(ROOT / ".env")

# Environment-first configuration (safer than hardcoding secrets)
API_KEY = os.getenv("API_KEY", "xxxx")
API_SECRET = os.getenv("API_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "xxxx")
MODE = os.getenv("MODE", "PAPER")

# DRY_RUN can be set via env to avoid placing live orders (true/1/yes)
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")

# For convenience, expose a helper to check if credentials appear configured
def has_valid_credentials():
	return API_KEY not in (None, "", "xxxx") and ACCESS_TOKEN not in (None, "", "xxxx")

import csv
from pathlib import Path
from datetime import datetime

LOG = Path(__file__).resolve().parents[1] / "logs"
LOG.mkdir(parents=True, exist_ok=True)
TRADES_FILE = LOG / "trades.csv"

def record_trade(symbol, side, qty, price, mode, status="FILLED", order_id=None, extra=None):
    header = ["timestamp", "symbol", "side", "qty", "price", "mode", "status", "order_id", "extra"]
    row = [datetime.utcnow().isoformat(), symbol, side, qty, price, mode, status, order_id or "", extra or ""]
    write_header = not TRADES_FILE.exists()
    with TRADES_FILE.open("a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)

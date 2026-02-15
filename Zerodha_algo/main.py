import sys
import signal
import pandas as pd
import time, datetime as dt
from utils.logger import get_logger

from config.credentials import *
from config.credentials import DRY_RUN
from config.settings import *
from strategies.indicators import add_indicators
from strategies.entry_exit import buy_signal, sell_signal
from risk.position_size import calculate_qty
from risk.risk_manager import can_trade
from execution.broker import place_live_order
from execution.paper_broker import place_paper_order
from utils.helpers import in_market_time

logger = get_logger("main")

try:
    from kiteconnect import KiteConnect
except Exception:
    logger.error("Missing dependency 'kiteconnect' in current interpreter %s", sys.executable)
    sys.exit(1)

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# quick auth check
from config.credentials import has_valid_credentials
if not has_valid_credentials():
    logger.error("API_KEY/ACCESS_TOKEN appear to be missing or placeholders. Fill .env or config/credentials.py and run generate_token.py to get a valid ACCESS_TOKEN.")
    sys.exit(1)
try:
    kite.profile()
except Exception as e:
    logger.error("Authentication failed: %s. Run generate_token.py to refresh your ACCESS_TOKEN.", e)
    sys.exit(1)

# graceful shutdown flag
SHOULD_STOP = False
def _handle_sig(signum, frame):
    global SHOULD_STOP
    logger.info("Received signal %s, shutting down...", signum)
    SHOULD_STOP = True

signal.signal(signal.SIGINT, _handle_sig)
signal.signal(signal.SIGTERM, _handle_sig)

tokens = {}
inst = pd.DataFrame(kite.instruments("NSE"))
available_symbols = []
for s in SYMBOLS:
    row = inst[inst.tradingsymbol == s]
    if row.empty:
        logger.warning("Instrument %s not found in NSE instruments; skipping symbol", s)
        continue
    tokens[s] = int(row.instrument_token.values[0])
    available_symbols.append(s)

# restrict SYMBOLS to those available
SYMBOLS = available_symbols

positions = {s: None for s in SYMBOLS}
entries = {}
trail_sl = {}
qtys = {s: 0 for s in SYMBOLS}

daily_pnl = 0
trade_count = 0
max_loss = CAPITAL * DAILY_MAX_LOSS

logger.info("Algo Started | Mode: %s", MODE)

while True:
    if SHOULD_STOP:
        logger.info("Shutdown requested; exiting main loop")
        break
    # try:
    #     if not in_market_time(
    #         dt.time(*START_TIME),
    #         dt.time(*END_TIME)
    #     ):
    #         time.sleep(30)
    #         continue

    #     if not can_trade(daily_pnl, max_loss, trade_count, MAX_TRADES_PER_DAY):
    #         logger.info("Trading stopped for the day")
    #         break

    #     for symbol in SYMBOLS:
    #         if SHOULD_STOP:
    #             logger.info("Shutting down main loop")
    #             break
    #     # try:
    #     #     data = kite.historical_data(
    #     #         tokens[symbol],
    #     #         dt.datetime.now() - dt.timedelta(days=5),
    #     #         dt.datetime.now(),
    #     #         TIMEFRAME
    #     #     )
    #     # except Exception as e:
    #     #     logger.warning("Error fetching historical data for %s: %s", symbol, e)
    #     #     continue

    #     df = add_indicators(pd.DataFrame(data), FAST_EMA, SLOW_EMA)
    #     if len(df) < 2:
    #         # not enough data yet
    #         continue
    #     last, prev = df.iloc[-1], df.iloc[-2]
    #     price = last.close

    #     if last.adx < ADX_THRESHOLD or abs(last.ai_score) < 0.05:
    #         continue

    #     if positions[symbol] is None:
    #         if buy_signal(prev, last):
    #             sl = price * (1 - TRAIL_SL_PCT/100)
    #             qty = calculate_qty(CAPITAL, RISK_PER_TRADE, price, sl)
    #             qtys[symbol] = qty

    #             try:
    #                 if MODE == "LIVE" and not DRY_RUN:
    #                     resp = place_live_order(kite, symbol, kite.TRANSACTION_TYPE_BUY, qty)
    #                     order_id = resp.get("order_id") if isinstance(resp, dict) else None
    #                     # confirm order status (best-effort)
    #                     try:
    #                         from execution.broker import confirm_order_status
    #                         status = confirm_order_status(kite, order_id)
    #                     except Exception:
    #                         status = None
    #                     try:
    #                         from utils.trade_logger import record_trade
    #                         record_trade(symbol, "BUY", qty, price=price, mode="LIVE", order_id=order_id, status=status or "OPEN")
    #                     except Exception:
    #                         logger.exception("Failed to record trade for %s after live order", symbol)
    #                 else:
    #                     place_paper_order(symbol, "BUY", qty)
    #                     try:
    #                         from utils.trade_logger import record_trade
    #                         record_trade(symbol, "BUY", qty, price=price, mode="PAPER", status="SIMULATED")
    #                     except Exception:
    #                         logger.exception("Failed to record paper BUY for %s", symbol)
    #             except Exception as e:
    #                 logger.error("Error placing entry order for %s: %s", symbol, e)
    #                 # do not set position state if order failed
    #             else:
    #                 positions[symbol] = "BUY"
    #                 entries[symbol] = price
    #                 trail_sl[symbol] = sl
    #                 trade_count += 1
    #                 logger.info("Entered BUY %s qty=%s price=%.2f sl=%.2f", symbol, qty, price, sl)

    #     elif positions[symbol] == "BUY":
    #         trail_sl[symbol] = max(trail_sl[symbol], price * (1 - TRAIL_SL_PCT/100))
    #         if price <= trail_sl[symbol]:
    #             qty = qtys.get(symbol, 0)
    #             pnl = (price - entries.get(symbol, price)) * qty
    #             daily_pnl += pnl

    #             try:
    #                 if MODE == "LIVE" and not DRY_RUN:
    #                     resp = place_live_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, qty)
    #                     order_id = resp.get("order_id") if isinstance(resp, dict) else None
    #                     try:
    #                         from execution.broker import confirm_order_status
    #                         status = confirm_order_status(kite, order_id)
    #                     except Exception:
    #                         status = None
    #                     try:
    #                         from utils.trade_logger import record_trade
    #                         record_trade(symbol, "SELL", qty, price=price, mode="LIVE", order_id=order_id, status=status or "OPEN")
    #                     except Exception:
    #                         logger.exception("Failed to record trade for %s after live exit", symbol)
    #                 else:
    #                     place_paper_order(symbol, "SELL", qty)
    #                     try:
    #                         from utils.trade_logger import record_trade
    #                         record_trade(symbol, "SELL", qty, price=price, mode="PAPER", status="SIMULATED")
    #                     except Exception:
    #                         logger.exception("Failed to record paper SELL for %s", symbol)
    #             except Exception as e:
    #                 logger.error("Error placing exit order for %s: %s", symbol, e)
    #             else:
    #                 logger.info("Exited SELL %s qty=%s price=%.2f pnl=%.2f", symbol, qty, price, pnl)

    #             # reset position state
    #             positions[symbol] = None
    #             entries.pop(symbol, None)
    #             trail_sl.pop(symbol, None)
    #             qtys[symbol] = 0

    

    time.sleep(60)

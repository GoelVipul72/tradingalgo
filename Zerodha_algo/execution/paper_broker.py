def place_paper_order(symbol, side, qty):
    from utils.logger import get_logger
    from utils.trade_logger import record_trade
    logger = get_logger("paper_broker")
    logger.info("PAPER ORDER | %s | %s | Qty %s", symbol, side, qty)
    # simulate an immediate filled trade at market price -- we don't have price here
    # caller should call record_trade with actual price, but as fallback, log qty and side
    record_trade(symbol, side, qty, price=0, mode="PAPER", status="SIMULATED")

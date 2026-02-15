def can_trade(daily_pnl, max_loss, trade_count, max_trades):
    if daily_pnl <= -max_loss:
        return False
    if trade_count >= max_trades:
        return False
    return True

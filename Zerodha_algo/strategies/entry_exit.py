def buy_signal(prev, last):
    return (
        prev.ema_fast < prev.ema_slow and
        last.ema_fast > last.ema_slow and
        last.close > last.vwap
    )

def sell_signal(prev, last):
    return (
        prev.ema_fast > prev.ema_slow and
        last.ema_fast < last.ema_slow and
        last.close < last.vwap
    )

import pandas as pd
import numpy as np

def add_indicators(df, fast, slow):
    df['ema_fast'] = df['close'].ewm(span=fast).mean()
    df['ema_slow'] = df['close'].ewm(span=slow).mean()

    tp = (df['high'] + df['low'] + df['close']) / 3
    df['vwap'] = (tp * df['volume']).cumsum() / df['volume'].cumsum()

    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(abs(df['high'] - df['close'].shift()),
                   abs(df['low'] - df['close'].shift()))
    )
    df['adx'] = df['tr'].rolling(14).mean()

    df['ai_score'] = (df['ema_fast'] - df['ema_slow']) / df['close']
    return df

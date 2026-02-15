import pandas as pd
from strategies.indicators import add_indicators


def test_add_indicators_basic():
    data = {
        "open": [100, 101, 102, 103, 104],
        "high": [101, 102, 103, 104, 105],
        "low": [99, 100, 101, 102, 103],
        "close": [100, 101, 102, 103, 104],
        "volume": [1000, 1100, 1200, 1300, 1400],
    }
    df = pd.DataFrame(data)
    out = add_indicators(df, fast=2, slow=3)
    assert "ema_fast" in out.columns
    assert "ema_slow" in out.columns
    assert "vwap" in out.columns
    assert "adx" in out.columns
    assert "ai_score" in out.columns
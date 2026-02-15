import pandas as pd
from strategies.entry_exit import buy_signal, sell_signal


def make_row(ema_fast, ema_slow, close, vwap=0):
    return pd.Series({"ema_fast": ema_fast, "ema_slow": ema_slow, "close": close, "vwap": vwap})


def test_buy_signal_true():
    prev = make_row(ema_fast=9, ema_slow=21, close=95, vwap=90)
    last = make_row(ema_fast=22, ema_slow=21, close=101, vwap=100)
    assert buy_signal(prev, last)


def test_buy_signal_false_when_not_cross():
    prev = make_row(ema_fast=10, ema_slow=9, close=95, vwap=90)
    last = make_row(ema_fast=11, ema_slow=9, close=101, vwap=100)
    assert not buy_signal(prev, last)


def test_sell_signal_true():
    prev = make_row(ema_fast=22, ema_slow=21, close=105, vwap=106)
    last = make_row(ema_fast=20, ema_slow=21, close=95, vwap=100)
    assert sell_signal(prev, last)


def test_sell_signal_false_when_not_cross():
    prev = make_row(ema_fast=9, ema_slow=21, close=95, vwap=100)
    last = make_row(ema_fast=10, ema_slow=21, close=101, vwap=100)
    assert not sell_signal(prev, last)

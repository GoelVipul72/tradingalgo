import datetime as dt

def in_market_time(start, end):
    now = dt.datetime.now().time()
    return start <= now <= end

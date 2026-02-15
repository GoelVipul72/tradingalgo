def calculate_qty(capital, risk_pct, entry, sl):
    # basic validation
    risk_amt = capital * risk_pct
    risk_per_unit = abs(entry - sl)
    if risk_per_unit == 0:
        # cannot compute qty; return minimum lot
        return 50

    # compute raw qty and round down to nearest 50-lot
    qty = int((risk_amt / risk_per_unit) / 50) * 50
    if qty <= 0:
        return 50
    return qty

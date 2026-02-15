from risk.position_size import calculate_qty


def test_calculate_qty_normal():
    qty = calculate_qty(capital=200000, risk_pct=0.01, entry=100, sl=90)
    # risk_amt = 2000, risk_per_unit=10 => raw = 200 => nearest 50 -> 200
    assert qty == 200


def test_calculate_qty_zero_risk_unit():
    qty = calculate_qty(capital=100000, risk_pct=0.01, entry=100, sl=100)
    # when entry == sl, should return minimum lot 50
    assert qty == 50


def test_calculate_qty_minimum():
    qty = calculate_qty(capital=1000, risk_pct=0.01, entry=100, sl=99)
    # risk_amt = 10, risk_per_unit=1 => raw = 10/50 -> 0 -> should return 50
    assert qty == 50

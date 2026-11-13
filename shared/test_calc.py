from calc import break_even, drr_metrics, unit_economics


def test_unit_profitable():
    r = unit_economics(
        price=2490, cogs=900, fee_pct=15, logistics=120, buyout_pct=85, ads=180, other=40
    )
    assert r.profit > 0
    assert r.margin_pct > 10
    assert r.level in ("ok", "warn")


def test_unit_loss():
    r = unit_economics(
        price=500, cogs=400, fee_pct=20, logistics=150, buyout_pct=50, ads=100, other=50
    )
    assert r.profit < 0
    assert r.level == "bad"


def test_drr():
    r = drr_metrics(25000, 120000, 48)
    assert abs(r.drr_pct - (25000 / 120000 * 100)) < 0.01
    assert r.cpo > 0
    assert r.roas > 1


def test_be():
    r = break_even(80000, 350, 50000)
    assert r.break_even_orders == 229
    assert r.target_orders == 372


if __name__ == "__main__":
    test_unit_profitable()
    test_unit_loss()
    test_drr()
    test_be()
    print("ok")

"""Shared unit-economics helpers for web parity and Telegram bot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UnitResult:
    profit: float
    margin_pct: float
    fee_rub: float
    logistics_eff: float
    costs: float
    verdict: str
    level: str  # ok | warn | bad


@dataclass
class DrrResult:
    drr_pct: float
    cpo: float
    roas: float
    verdict: str
    level: str


@dataclass
class BeResult:
    break_even_orders: int
    target_orders: int
    verdict: str


def unit_economics(
    price: float,
    cogs: float,
    fee_pct: float,
    logistics: float,
    buyout_pct: float,
    ads: float = 0.0,
    other: float = 0.0,
) -> UnitResult:
    buyout = max(buyout_pct, 1.0) / 100.0
    fee_rub = price * (fee_pct / 100.0)
    logistics_eff = logistics + (logistics * (1.0 - buyout)) / buyout
    costs = cogs + fee_rub + logistics_eff + ads + other
    profit = price - costs
    margin = (profit / price * 100.0) if price > 0 else 0.0

    if margin >= 25:
        verdict, level = "Сильная карточка — можно масштабировать трафик.", "ok"
    elif margin >= 12:
        verdict, level = "Рабочая маржа. Следи за ДРР и выкупом.", "ok"
    elif margin >= 0:
        verdict, level = "Тонкая экономика. Режь комиссию/логистику или поднимай цену.", "warn"
    else:
        verdict, level = "Убыточная модель — не закупай партию на этих цифрах.", "bad"

    return UnitResult(profit, margin, fee_rub, logistics_eff, costs, verdict, level)


def drr_metrics(budget: float, revenue: float, orders: float) -> DrrResult:
    drr = (budget / revenue * 100.0) if revenue > 0 else 0.0
    cpo = (budget / orders) if orders > 0 else 0.0
    roas = (revenue / budget) if budget > 0 else 0.0
    if drr <= 12:
        verdict, level = "Отличный ДРР — можно повышать бюджет.", "ok"
    elif drr <= 20:
        verdict, level = "Нормальный ДРР для теста. Оптимизируй ставки.", "warn"
    else:
        verdict, level = "ДРР высокий — сужай запросы или улучшай карточку.", "bad"
    return DrrResult(drr, cpo, roas, verdict, level)


def break_even(fixed: float, unit_profit: float, target_profit: float = 0.0) -> BeResult:
    unit = max(unit_profit, 1.0)
    zero = int(-(-fixed // unit))  # ceil
    goal = int(-(-(fixed + target_profit) // unit))
    verdict = (
        f"Нужно ≈{zero} заказов/мес до нуля и ≈{goal} заказов "
        f"для цели {target_profit:.0f} ₽ прибыли."
    )
    return BeResult(zero, goal, verdict)


def fmt_money(v: float) -> str:
    return f"{v:,.0f} ₽".replace(",", " ")

"""
SellerKit Telegram bot — unit economics / DRR / break-even for WB·Ozon sellers.
Needs only BOT_TOKEN in .env (see .env.example). Optional AFFILIATE_* for monetization.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from calc import break_even, drr_metrics, fmt_money, unit_economics  # noqa: E402

load_dotenv(Path(__file__).with_name(".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
AFFILIATE_URL = os.getenv("AFFILIATE_URL", "").strip()
AFFILIATE_LABEL = os.getenv("AFFILIATE_LABEL", "Партнёрский инструмент").strip()

WAITING: dict[int, str] = {}

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Юнит-экономика"), KeyboardButton(text="📣 ДРР")],
        [KeyboardButton(text="🎯 Точка безубыточности"), KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)


def help_text() -> str:
    lines = [
        "SellerKit — калькуляторы для селлеров WB / Ozon / Я.Маркет.",
        "",
        "Команды:",
        "/unit цена себес комиссия% логистика выкуп% [реклама] [прочее]",
        "  пример: /unit 1990 650 15 120 70 80 0",
        "/drr бюджет выручка заказы",
        "  пример: /drr 15000 90000 45",
        "/be фикс маржа_на_заказ цель_прибыли",
        "  пример: /be 80000 350 100000",
        "",
        "Или жми кнопки ниже — бот попросит цифры по шагам.",
    ]
    if AFFILIATE_URL:
        lines += ["", f"🔗 {AFFILIATE_LABEL}: {AFFILIATE_URL}"]
    return "\n".join(lines)


async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я SellerKit — считаю маржу, ДРР и безубыточность для маркетплейсов.\n\n"
        + help_text(),
        reply_markup=MAIN_KB,
    )


async def cmd_help(message: Message) -> None:
    await message.answer(help_text(), reply_markup=MAIN_KB)


async def cmd_unit(message: Message) -> None:
    parts = (message.text or "").split()[1:]
    if len(parts) < 5:
        WAITING[message.from_user.id] = "unit"
        await message.answer(
            "Пришли одной строкой:\n"
            "<code>цена себес комиссия% логистика выкуп% [реклама] [прочее]</code>\n"
            "пример: <code>1990 650 15 120 70 80 0</code>",
            parse_mode="HTML",
        )
        return
    await _reply_unit(message, parts)


async def cmd_drr(message: Message) -> None:
    parts = (message.text or "").split()[1:]
    if len(parts) < 3:
        WAITING[message.from_user.id] = "drr"
        await message.answer(
            "Пришли: <code>бюджет выручка заказы</code>\nпример: <code>15000 90000 45</code>",
            parse_mode="HTML",
        )
        return
    await _reply_drr(message, parts)


async def cmd_be(message: Message) -> None:
    parts = (message.text or "").split()[1:]
    if len(parts) < 2:
        WAITING[message.from_user.id] = "be"
        await message.answer(
            "Пришли: <code>фикс_расходы прибыль_с_заказа [цель_прибыли]</code>\n"
            "пример: <code>80000 350 100000</code>",
            parse_mode="HTML",
        )
        return
    await _reply_be(message, parts)


async def on_text(message: Message) -> None:
    text = (message.text or "").strip()
    uid = message.from_user.id if message.from_user else 0

    if text == "📦 Юнит-экономика":
        WAITING[uid] = "unit"
        await message.answer(
            "Цифры одной строкой:\n<code>цена себес комиссия% логистика выкуп% [реклама] [прочее]</code>",
            parse_mode="HTML",
        )
        return
    if text == "📣 ДРР":
        WAITING[uid] = "drr"
        await message.answer("Цифры: <code>бюджет выручка заказы</code>", parse_mode="HTML")
        return
    if text == "🎯 Точка безубыточности":
        WAITING[uid] = "be"
        await message.answer(
            "Цифры: <code>фикс прибыль_с_заказа [цель]</code>", parse_mode="HTML"
        )
        return
    if text == "ℹ️ Помощь":
        await cmd_help(message)
        return

    mode = WAITING.pop(uid, None)
    if not mode:
        await message.answer("Жми кнопку меню или /help", reply_markup=MAIN_KB)
        return
    parts = text.replace(",", ".").split()
    if mode == "unit":
        await _reply_unit(message, parts)
    elif mode == "drr":
        await _reply_drr(message, parts)
    else:
        await _reply_be(message, parts)


def _floats(parts: list[str], n: int) -> list[float] | None:
    try:
        vals = [float(p) for p in parts[:n]]
        if len(vals) < n:
            return None
        return vals
    except ValueError:
        return None


async def _reply_unit(message: Message, parts: list[str]) -> None:
    vals = _floats(parts, 5)
    if not vals:
        await message.answer("Не разобрал числа. Нужно минимум 5 цифр.")
        return
    try:
        ads = float(parts[5]) if len(parts) > 5 else 0.0
        other = float(parts[6]) if len(parts) > 6 else 0.0
    except ValueError:
        await message.answer("Хвост строки должен быть числами.")
        return
    r = unit_economics(vals[0], vals[1], vals[2], vals[3], vals[4], ads, other)
    icon = {"ok": "✅", "warn": "⚠️", "bad": "❌"}[r.level]
    await message.answer(
        f"{icon} <b>Юнит-экономика</b>\n"
        f"Прибыль: <b>{fmt_money(r.profit)}</b>\n"
        f"Маржа: <b>{r.margin_pct:.1f}%</b>\n"
        f"Комиссия: {fmt_money(r.fee_rub)}\n"
        f"Логистика с учётом выкупа: {fmt_money(r.logistics_eff)}\n"
        f"Всего затрат: {fmt_money(r.costs)}\n\n"
        f"{r.verdict}",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )
    if AFFILIATE_URL:
        await message.answer(f"🔗 {AFFILIATE_LABEL}\n{AFFILIATE_URL}")


async def _reply_drr(message: Message, parts: list[str]) -> None:
    vals = _floats(parts, 3)
    if not vals:
        await message.answer("Нужны 3 числа: бюджет выручка заказы")
        return
    r = drr_metrics(vals[0], vals[1], vals[2])
    icon = {"ok": "✅", "warn": "⚠️", "bad": "❌"}[r.level]
    await message.answer(
        f"{icon} <b>ДРР</b>\n"
        f"ДРР: <b>{r.drr_pct:.1f}%</b>\n"
        f"CPO: {fmt_money(r.cpo)}\n"
        f"ROAS: {r.roas:.2f}×\n\n"
        f"{r.verdict}",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


async def _reply_be(message: Message, parts: list[str]) -> None:
    vals = _floats(parts, 2)
    if not vals:
        await message.answer("Нужны минимум 2 числа: фикс и прибыль с заказа")
        return
    try:
        target = float(parts[2]) if len(parts) > 2 else 0.0
    except ValueError:
        target = 0.0
    r = break_even(vals[0], vals[1], target)
    await message.answer(
        f"🎯 <b>Безубыточность</b>\n"
        f"До нуля: <b>{r.break_even_orders}</b> заказов/мес\n"
        f"До цели: <b>{r.target_orders}</b> заказов/мес\n\n"
        f"{r.verdict}",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN не задан. Создай sellerkit/bot/.env из .env.example "
            "(токен от @BotFather) и перезапусти."
        )
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_unit, Command("unit"))
    dp.message.register(cmd_drr, Command("drr"))
    dp.message.register(cmd_be, Command("be"))
    dp.message.register(on_text, F.text)
    print("SellerKit bot polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

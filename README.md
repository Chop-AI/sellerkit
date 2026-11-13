# SellerKit

Бесплатные калькуляторы юнит-экономики для селлеров Wildberries / Ozon / Яндекс Маркет.

- **Web:** `web/` — статика, деплой на GitHub Pages
- **Telegram:** `bot/` — те же формулы, нужен только `BOT_TOKEN`
- **Shared:** `shared/calc.py` — общие расчёты

## Web

Открой `web/index.html` локально или Pages URL репозитория.

Опционально в `web/config.js`:
- `affiliateUrl` / `affiliateLabel`
- `telegramBot` (username без @)

## Telegram bot

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # впиши BOT_TOKEN от @BotFather
python bot.py
```

Команды: `/unit` `/drr` `/be` `/help`

## Монетизация без ручных продаж

1. Трафик на сайт / бота (SEO, Telegram-каналы селлеров)
2. Партнёрская ссылка в `AFFILIATE_URL` / `config.js`
3. Позже: Telegram Stars, РСЯ/AdSense ID

Человеку достаточно один раз выдать `BOT_TOKEN` и при желании партнёрский URL.

# Gift Crafting Optimizer — Full Product (Zero Capital)

## What it is
A Telegram Mini App that computes Star Gift crafting probabilities from documented rules.
Runs entirely in the browser (no backend, no API keys, no capital). Optional bot wrapper.

## Files
- gift_calc.py / test_gift_calc.py — backend logic + 15 tests (all pass)
- gift_calc.js — client-side port of the same logic (verified)
- index.html — local web version (with Python backend)
- miniapp.html — Telegram Mini App version (static, no backend)
- app.py — optional local server for index.html
- bot.py — minimal Telegram bot (stdlib only) that opens the Mini App
- fragment_sample.json — static market sample (59 Gram prices, Oct 2026)
- README.md — this file

## Run locally (Windows)
Option A — local web app (with backend):
  cd C:\Users\PC\telegram-gift-engine
  python app.py
  open http://127.0.0.1:8765

Option B — static Mini App (no backend):
  cd C:\Users\PC\telegram-gift-engine
  python -m http.server 8766
  open http://127.0.0.1:8766/miniapp.html

## Tests
  cd C:\Users\PC\telegram-gift-engine
  python -c "import test_gift_calc as t; [getattr(t,n)() for n in dir(t) if n.startswith('test_')]; print('ALL PASSED')"
  node --check gift_calc.js && echo "JS OK"

## Deploy as Telegram Mini App (free, zero capital)
1. Host miniapp.html + gift_calc.js on a free static host (GitHub Pages / Netlify / Cloudflare Pages).
2. Create a bot via @BotFather, get token.
3. Set env vars and run bot:
   set BOT_TOKEN=your_token_here
   set MINIAPP_URL=https://dockfixlabs.github.io/gift-crafting-optimizer/miniapp.html
   python bot.py
4. Send /start to your bot, tap "Open Calculator".

## Market data
- fragment_sample.json: 59 recent sold prices from Fragment (Gram). Static snapshot, not live. Not Stars.
- No live feeds, no alerts, no buy/sell execution.

## What works
- Crafting success probability (sum of craft_chance_permille, clamped, UI rounding per docs)
- Attribute persistence probability (config rows, grouping by ID)
- Input validation (count 1-4, same base id, permille 0-1000, config shape)
- Multi-scenario comparison (index.html) / single scenario (miniapp.html)
- Warnings: estimates only, inputs burned, no profit guarantee

## What is experimental
- Config values are user-provided (not fetched from live Telegram client)
- Market sample is a static snapshot

## What is NOT implemented
- No Telegram API integration for reading user collectibles (Bot API lacks craft fields)
- No live price feeds, no alerts, no buy/sell execution
- No user accounts, no payments
- No patent claims, no "first of its kind" claims

## Next step to test demand
1. Deploy miniapp to GitHub Pages (free).
2. Create bot, share link in 3 Telegram gift communities.
3. Collect feedback for 2 weeks.
4. If >=10% of active users say they'd pay, build MTProto Mini App + live data layer.
5. Otherwise, keep as free tool or stop.

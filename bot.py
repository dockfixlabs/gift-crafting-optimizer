"""Telegram bot for Gift Crafting Optimizer Mini App.

Uses aiogram 3.x for async, robust polling with auto-retry.
Requires: BOT_TOKEN env var, MINIAPP_URL env var.
"""
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MINIAPP_URL = os.environ.get("MINIAPP_URL", "https://dockfixlabs.github.io/gift-crafting-optimizer/miniapp.html")

HELP_TEXT = (
    "Gift Crafting Optimizer\n\n"
    "Computes Telegram Star Gift crafting probabilities from documented rules.\n"
    "No login required. No trading. Probabilities are estimates.\n\n"
    "Commands:\n"
    "/start - Open the calculator\n"
    "/about - About this bot\n"
    "/help - This message\n"
    "/stats - Usage stats"
)

ABOUT_TEXT = (
    "Gift Crafting Optimizer v2.0\n"
    "Evidence-based. No hype. No patent claims.\n"
    "Source: core.telegram.org/api/gifts\n"
    "Market data: static sample (Fragment, Oct 2026).\n"
    "Built with: aiogram 3.x, PWA, Telegram Web App SDK, liquid glass UI."
)

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open Calculator", web_app=WebAppInfo(url=MINIAPP_URL))]
    ])
    await message.answer(
        "Gift Crafting Optimizer - compute crafting probabilities from documented Telegram rules.",
        reply_markup=kb,
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT)


@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    await message.answer(ABOUT_TEXT)


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await message.answer("Stats: coming soon. Use /start to open the calculator.")


@dp.message()
async def handle_other(message: types.Message):
    await message.answer("Unknown command. Use /help.")


async def main():
    if not BOT_TOKEN:
        print("ERROR: set BOT_TOKEN env var")
        return
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_description(description="Computes Telegram Star Gift crafting probabilities from documented rules. Evidence-based. No hype.")
    await bot.set_my_short_description(short_description="Star Gift crafting probability calculator")
    await bot.set_my_commands(commands=[
        BotCommand(command="start", description="Open the calculator"),
        BotCommand(command="help", description="Help message"),
        BotCommand(command="about", description="About this bot"),
    ])
    print("Bot running (aiogram 3.x). Send /start to your bot in Telegram.")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())

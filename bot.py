import asyncio
import logging
import sys
import os

# Windows UTF-8 console output support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

import config
from database import init_db
from handlers import start, about, contacts, location, menu, feedback, admin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def start_web_healthcheck():
    port_str = os.getenv("PORT")
    if not port_str:
        return None
    try:
        port = int(port_str)
        app = web.Application()
        async def ping_handler(request):
            return web.Response(text="👑 Alixan Fast Food Telegram Bot is Running 24/7!", content_type="text/plain", charset="utf-8")
        app.router.add_get("/", ping_handler)
        app.router.add_get("/ping", ping_handler)
        app.router.add_get("/health", ping_handler)
        app.router.add_route("*", "/{tail:.*}", ping_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"🌐 Cloud health check server listening on port {port}")
        return runner
    except Exception as e:
        logger.warning(f"Failed to start healthcheck server: {e}")
        return None

async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🌟 Botni qayta ishga tushirish"),
        BotCommand(command="about", description="ℹ️ Biz haqimizda"),
        BotCommand(command="contacts", description="📞 Telefon va buyurtma"),
        BotCommand(command="location", description="📍 Manzil va ish vaqti"),
        BotCommand(command="delivery", description="🛵 Yetkazib berish"),
        BotCommand(command="admin", description="⚙️ Admin boshqaruv paneli")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

async def main():
    logger.info("Initializing Alixan Fast Food Telegram Bot...")

    # Initialize Database
    await init_db()
    logger.info("Database initialized successfully.")

    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "="*60 + "\n"
            "⚠️ XATOLIK: Bot tokeni topilmadi!\n"
            "Iltimos, .env faylini oching va BOT_TOKEN o'rniga o'z bot tokeningizni qo'ying:\n"
            "BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n"
            "="*60 + "\n"
        )
        sys.exit(1)

    # Initialize Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register all routers
    dp.include_router(start.router)
    dp.include_router(about.router)
    dp.include_router(contacts.router)
    dp.include_router(location.router)
    dp.include_router(menu.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)

    # Set commands
    await set_default_commands(bot)

    # Drop pending updates to avoid spam on restart
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    me = await bot.get_me()
    logger.info(f"✅ Bot muvaffaqiyatli ishga tushdi: @{me.username} ({me.first_name})")
    print(f"\n🚀 Alixan Fast Food Bot ishga tushdi: https://t.me/{me.username}\n")

    web_runner = await start_web_healthcheck()

    # Start Polling
    try:
        await dp.start_polling(bot)
    finally:
        if web_runner:
            await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

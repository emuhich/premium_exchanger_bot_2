from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="🏦Главное меню 🏦",
        ),
        BotCommand(
            command="support",
            description="🆘 Поддержка 🆘",
        ),
        BotCommand(
            command="rules",
            description="📝 Правила 📝",
        ),
        BotCommand(
            command="policy",
            description="🕵️‍♂️ AML/KYC политика 🕵️‍♂️",
        ),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

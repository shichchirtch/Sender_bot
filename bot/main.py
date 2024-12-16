import asyncio
from command_handlers import ch_router
from bot_instance import bot, bot_storage_key, dp
from aiogram_dialog import setup_dialogs
from start_menu import set_main_menu
from base_dialog import start_dialog, base_dialog
from postgres_table import init_models
from help_dialog import dialog_help
from admin_dialog import admin_dialog
from anketa_dialog import anketa_dialog


async def main():
    await init_models()

    dp.startup.register(set_main_menu)
    await dp.storage.set_data(key=bot_storage_key, data={})

    dp.include_router(ch_router)
    dp.include_router(start_dialog)
    dp.include_router(base_dialog)
    dp.include_router(anketa_dialog)
    dp.include_router(dialog_help)
    dp.include_router(admin_dialog)



    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    await dp.start_polling(bot)

asyncio.run(main())
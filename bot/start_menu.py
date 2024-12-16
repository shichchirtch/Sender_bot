from aiogram.types import BotCommand


async def set_main_menu(bot):
    main_menu_commands = [

        BotCommand(command='/help',
                   description='go to personal chatting')

    ]
    await bot.set_my_commands(main_menu_commands)
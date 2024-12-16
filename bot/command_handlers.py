from aiogram import Router
import asyncio
from aiogram.filters import CommandStart, Command
from filters import IS_ADMIN
from aiogram.fsm.context import FSMContext
from bot_instance import dp, bot_storage_key, START_DIAL, HELP_DIAL
from admin_dialog import ADMIN
from postgres_functions import check_user_in_table, insert_new_user_in_table
from aiogram_dialog.api.entities.modes import StartMode
from aiogram.types import Message
from aiogram_dialog import DialogManager



ch_router = Router()

@ch_router.message(CommandStart())
async def command_start_process(message:Message, dialog_manager: DialogManager, state:FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        print('start if works')
        await insert_new_user_in_table(user_id, user_name)
        await state.set_data({'line':'', 'selector':'1','anketa':'','done':False})
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        bot_dict[message.from_user.id] = {}  # Создаю пустой словарь для заметок юзера
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=f'👋\n\n<b>Привет, {message.from_user.first_name}!</b>\n'
           'Это  бот для участия в различных социальных активностях ! Нажми на кнопку START')

        await dialog_manager.start(state=START_DIAL.start, mode=StartMode.RESET_STACK)
    else:
        print('start else works')
        await insert_new_user_in_table(user_id, user_name)
        await dialog_manager.start(state=START_DIAL.start, mode=StartMode.RESET_STACK)
        await message.answer(text='Нажата кнопка старт')
        await message.delete()


@ch_router.message(Command('help'))
async def basic_menu_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=HELP_DIAL.erst)
    await asyncio.sleep(1)
    await message.delete()


@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ADMIN.first)
    await asyncio.sleep(1)
    await message.delete()






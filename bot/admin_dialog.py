from aiogram_dialog import Dialog, Window
from bot_instance import dp, bot_storage_key
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Next
from aiogram_dialog.widgets.input import  MessageInput
from aiogram.types import CallbackQuery, Message, FSInputFile, User
from aiogram_dialog import DialogManager
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
import asyncio
import os
from postgres_functions import return_selector, get_user_count

class ADMIN(StatesGroup):
    first = State()
    accept_msg = State()
    admin_send_msg = State()


SURVEY_FILE_PATH = "./baza.txt"
SURVEY_CSV_FILE_PATH = "./user_surveys.csv"
SURVEY_CSV_FILE_PATH_OFFLINE = "./user_offline_2.csv"

# Функция для отправки файла администратору
async def send_survey_file(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    """Отправляет файл с анкетами администратору"""
    if not os.path.exists(SURVEY_FILE_PATH):
        await callback.message.answer("Файл с анкетами пока не создан.")
        return
    # Отправляем файл администратору
    survey_file = FSInputFile(SURVEY_FILE_PATH)
    await callback.bot.send_document(chat_id=-4776092700, document=survey_file)

    if os.path.exists(SURVEY_CSV_FILE_PATH):
        survey_csv_file = FSInputFile(SURVEY_CSV_FILE_PATH)
        await callback.bot.send_document(chat_id=-4776092700,document=survey_csv_file)

    if os.path.exists(SURVEY_CSV_FILE_PATH_OFFLINE):
        survey_csv_offline_file = FSInputFile(SURVEY_CSV_FILE_PATH_OFFLINE)
        await callback.bot.send_document(chat_id=-4776092700, document=survey_csv_offline_file)

async def admin_exit(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()

async def get_skolko(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    taily_users = await get_user_count()
    # print('taily_users = ', taily_users)
    getter_data = {'skolko': f'⏪  👮🏼‍♂️🧑🏼‍🚒👩🏻👨🏼‍🦱👩🏽‍🦱   {taily_users}'}
    return getter_data

async def send_admin_message(msg:Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    admin_msg = msg.text.strip()
    admin_selector = admin_msg[0]
    # print('accepet_admin_message works')
    # print('admin selector = ', admin_selector, type(admin_selector))
    counter = 0
    users_db  = await dp.storage.get_data(key=bot_storage_key)
    # print('user_db = ', users_db)
    if admin_selector not in '12345678':
        rest_admin_msg = admin_msg
        for user in users_db.keys():
            await msg.bot.send_message(chat_id=int(user), text=rest_admin_msg)
            counter+=1
            await asyncio.sleep(0.2)
    else:
        rest_admin_msg = admin_msg[1:]
        for user in users_db.keys():
            # print('user = ', user)
            selector = await return_selector(int(user))
            # print('user_selector = ', selector)
            if selector == admin_selector:
                await msg.bot.send_message(chat_id=user, text=rest_admin_msg)
                counter += 1
                await asyncio.sleep(0.2)

    await msg.answer(f'Рассылка завершена\n\nЧисло отпраленных сообщений = {counter}')
    await dialog_manager.back()

async def send_code(cb:CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    # print('send_code works')
    counter = 0
    users_db = await dp.storage.get_data(key=bot_storage_key)
    # print('users_db = ', users_db)
    for user in users_db.keys():
        # print('user = ', user)
        selector = await return_selector(int(user))
        if selector == 'wait':
            await cb.bot.send_message(chat_id=user, text='Отправьте мне код 2025')
            counter+=1
            await asyncio.sleep(0.2)

    await cb.message.answer(f'Теперь заполнившие анкету могут получать сообщения\n\nЧисло отпраленных сообщений = {counter}')
    await dialog_manager.back()


admin_dialog = Dialog(
    Window(
        Const('Напишите сообщения для той или иной группы участников. Начнинайте сообщение с '
              '\n\n<b>2</b> - Если хотите отправить сообщение тем кто заинтересовался'
              '\n\n<b>3</b>  - Если хотите отправить сообщение тем кто  заполняет анкету'
              '\n\n<b>4</b> - Если хотите отправить сообщение тем кто заполнил анкету и ждёт адрес отеля'
              '\n\n<b>5</b> - Если хотите отправить сообщение тем кто ждёт номер зала'
              '\n\n<b>6</b> - Если хотите отправить сообщение тем кто ждёт программу сессии'
              '\n\n<b>7</b> - Если хотите отправить сообщение тем прошел регистрацию'
              '\n\n<b>8</b> - Если хотите отправить сообщение тем кто ждёт работчие документы'
              '\n\n<b>1</b> - Если хотите отправить сообщение тем кто Закончил алгоритм работы с ботом'
              '\n\nЕсли хотите отправить сообщение всем стартовавшим бота - просто отправьте сообщение'
              '\n\n🟣'),
        Button(
            Const('Загрузить файл с базой анкет'),
            id='get_baza',
            on_click=send_survey_file
        ),
        Button(
            Const('Отправить код тем кто заполнил анкету'),
            id='send_code',
            on_click=send_code
        ),
        Button(
            text=Format('{skolko}'),
            id='exit',
            on_click=admin_exit),

        Next(
            text=Const('Написать сообщение'),
            id='send_msg'),
        state=ADMIN.first,
        getter=get_skolko,
    ),
    Window(  # Окно принимающее содержание сообщение
        Const(text='введите текст сообщения'),
        MessageInput(
            func=send_admin_message,
            content_types=ContentType.TEXT,
        ),
        state=ADMIN.accept_msg
    ),
    # Window(
    #     Const('Отправить сообщуху'),
    #     Button(
    #         text=Const('Отправить сообщение юзерам'),
    #         id='send_msg',
    #         on_click=sending_msg),
    #     state=ADMIN.admin_send_msg)

)
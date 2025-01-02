from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Group, Row, Cancel, Back, Next
from aiogram_dialog.api.entities.modes import ShowMode
from aiogram.fsm.state import State, StatesGroup
import asyncio
from bot_instance import dp, bot_storage_key, BASE_DIAL
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput, TextInput
from postgres_functions import (set_selector,
                                insert_line, insert_anketa, insert_done)
import os
import csv
import re



# Путь к файлу для хранения анкет
SURVEY_FILE_PATH = "./baza.txt"
SURVEY_CSV_FILE_PATH = "./user_surveys.csv"
SURVEY_CSV_FILE_PATH_OFFLINE = "./user_offline_2.csv"


class ANKETA(StatesGroup):
    fio = State()
    org = State()
    soglasie = State()
    line = State()
    roud_expensions = State()
    hotel_expensions = State()
    invoice = State()
    time_arriving = State()
    time_departure = State()


def fio_check(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError
    pattern = r"^[a-zA-Zа-яА-ЯёЁ\s]+$"
    res = bool(re.fullmatch(pattern, name))
    if res:
        return name
    else:
        raise ValueError


def time_check(time: str) -> str:
    if isinstance(time, str):
        return time
    raise ValueError


async def append_to_file(content: str, file_path: str = SURVEY_FILE_PATH):
    """Функция для добавления строки в файл"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Убедимся, что директория существует
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content + "\n")

async def append_to_csv(data: dict, file_path: str = SURVEY_CSV_FILE_PATH):
    """Функция для добавления данных в CSV файл"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Убедимся, что директория существует
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["fio", "org", "line", "first_name", "last_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Записываем заголовки, если файл создаётся впервые

        writer.writerow(data)  # Записываем данные

async def append_offline_to_csv(data: dict, file_path: str = SURVEY_CSV_FILE_PATH_OFFLINE):
    """Функция для добавления данных в CSV файл"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Убедимся, что директория существует
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["fio", "org", "way_pay", "hotel_pay", "tickets", "arrival", "departure"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Записываем заголовки, если файл создаётся впервые

        writer.writerow(data)  # Записываем данные


async def message_not_text_handler(message: Message, widget: MessageInput,
                                   dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer('Я могу принять только текстовое сообщение')


async def correct_fio_handler(message: Message, widget: ManagedTextInput,
                              manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер принимает ФИО"""
    print('fio = ', message.text)
    fio = message.text.strip()
    manager.dialog_data['fio'] = fio
    await set_selector(message.from_user.id, '3')
    manager.show_mode = ShowMode.SEND
    await message.delete()
    await manager.next()


async def go_to_3_wind(message: Message, widget: ManagedTextInput,
                       manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер принимает название организации"""
    org = message.text.strip()
    manager.dialog_data['org'] = org
    manager.show_mode = ShowMode.DELETE_AND_SEND
    await message.delete()
    await manager.next()


async def error_fio_handler(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            error: ValueError):
    await message.answer(text='Некорректное ФИО')  # Вы введи неверный id попробуйте ещё раз
    await asyncio.sleep(1)


async def arrival_time(message: Message, widget: ManagedTextInput,
                       manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер Время прибытия"""
    arrival = message.text.strip()
    manager.dialog_data['arrival'] = arrival
    manager.show_mode = ShowMode.SEND
    await message.delete()
    await manager.next()


async def online_handler(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['line'] = 'online'
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_dict = bot_dict[str(cb.from_user.id)]  # Получаю базу напоминаний юзера
    # await state.set_data({'fio': '', 'way_pay': '', 'hotel_pay': '', 'tickets': '', 'arrive': '' })
    fio = us_dict['fio'] = manager.dialog_data['fio']
    org = us_dict['org'] = manager.dialog_data['org']
    line = us_dict['line'] = 'online'
    # await dp.storage.update_data(key=bot_storage_key, data=us_dict)
    await insert_line(cb.from_user.id, 'online')

    stroka = (f'<b>Анкета Юзера </b> {cb.from_user.first_name}, {cb.from_user.last_name}'
              f'\n\nФИО - {fio},\n\n'
              f'<b>Организация</b> - {org},\n\n'
              f'<b>Online-Offline</b> - {line},\n\n')
    await cb.bot.send_message(chat_id=-4776092700, text=stroka)

    # Сохраняем анкету в файл
    await append_to_file(stroka.replace("<b>", "").replace("</b>", ""))

    # Сохраняем анкету в CSV файл
    csv_data = {
        "fio": fio,
        "org": org,
        "line": line,
        "first_name": cb.from_user.first_name,
        "last_name": cb.from_user.last_name,
    }
    await append_to_csv(csv_data)
    await insert_done(cb.from_user.id)
    await insert_anketa(cb.from_user.id, stroka)
    await cb.message.answer(
        'Спасибо, что заполнили анкету, оставайтесь со мной на связи. Я пришлю вам сообщение с информацией о месте проведения конференции ближе к дате концеренции 21.12.2024.')
    await set_selector(cb.from_user.id, '8')
    manager.show_mode = ShowMode.SEND
    await manager.start(BASE_DIAL.five)


async def offline_handler(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['line'] = 'Лично приеду'
    print('offline handler works')

    # manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()


async def want_way_payment(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['way_pay'] = 'Да'
    # manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()


async def do_not_want_way_payment(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['way_pay'] = 'Нет'
    # manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()


async def want_hotel_payment(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['hotel_pay'] = 'Да'
    # manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()


async def do_not_want_hotel_payment(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    manager.dialog_data['hotel_pay'] = 'Нет'
    # manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()


async def on_photo_sent(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    print('on_photo_sent works')
    foto_id = message.photo[-1].file_id
    dialog_manager.dialog_data['foto_id'] = foto_id
    await message.delete()
    await dialog_manager.next()


async def message_not_foto_handler(message: Message, widget: MessageInput,
                                   dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer('Я могу принять сейчас только фото')


async def go_to_arriving_time(cb: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    print('on_photo_sent works')
    manager.dialog_data['foto_id'] = ''
    await manager.next()


async def anketa_finished(cb: CallbackQuery, widget: Button,
                          manager: DialogManager, *args, **kwargs):
    print('anketa_finished works')
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_dict = bot_dict[str(cb.from_user.id)]  # Получаю базу напоминаний юзера
    print('226 us_dict = ', us_dict)
    # await state.set_data({'fio': '', 'way_pay': '', 'hotel_pay': '', 'tickets': '', 'arrive': '' })

    fio = us_dict['fio'] = manager.dialog_data['fio']
    org = us_dict['org'] = manager.dialog_data['org']
    line = us_dict['line'] = manager.dialog_data['line']
    way_pay = us_dict['way_pay'] = manager.dialog_data['way_pay']
    hotel_pay = us_dict['hotel_pay'] = manager.dialog_data['hotel_pay']
    tickets = us_dict['tickets'] = manager.dialog_data['foto_id']
    await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
    if not tickets:
        stroka = (f'<b>Анкета Юзера </b> {cb.from_user.first_name}, {cb.from_user.last_name}'
                  f'\n\nФИО - {fio},\n\n'
                  f'<b>Организация</b> - {org},\n\n'
                  f'<b>Online-Offline</b> - {line},\n\n'
                  f'<b>Оплата проезда</b> - {way_pay},\n\n'
                  f'<b>Оплата Отеля</b> - {hotel_pay},\n\n')
        await cb.bot.send_message(chat_id=-4776092700 , text=stroka)
    else:
        stroka = (f'Анкета Юзера {cb.from_user.first_name}, {cb.from_user.last_name}'
                  f'\n\nФИО - {fio},\n\n'
                  f'<b>Организация</b> - {org},\n\n'
                  f'<b>Online-Offline</b> - {line},\n\n'
                  f'<b>Фото билетов отпралвены</b>,\n\n'
                  f'Оплата проезда - {way_pay},\n\n'
                  f'Оплата Отеля - {hotel_pay},\n\n')
        await cb.bot.send_photo(chat_id=-4776092700 , photo=tickets, caption=stroka)
# -4687975968

# -4776092700 - id groupp
    await append_to_file(stroka.replace("<b>", "").replace("</b>", ""))
    # Сохраняем анкету в CSV файл
    csv_data = {
        "fio": fio,
        "org": org,
        "way_pay":way_pay,
        "hotel_pay":hotel_pay,
        "tickets":tickets,
    }
    await append_offline_to_csv(csv_data)

    await insert_anketa(cb.from_user.id, stroka)
    await insert_done(cb.from_user.id)
    if  hotel_pay != 'Нет':
        await set_selector(cb.from_user.id, '4')
        await cb.message.answer(
            'Спасибо, что заполнили анкету, оставайтесь со мной на связи.')
        await asyncio.sleep(0.5)
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.start(BASE_DIAL.hotel_adres)

    else:
        await set_selector(cb.from_user.id, '5')
        await cb.message.answer(
            'Спасибо, что заполнили анкету, оставайтесь со мной на связи.')
        await asyncio.sleep(0.5)
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.start(BASE_DIAL.zal_number)



async def error_check_time(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                           error: ValueError):
    await message.answer(text='Некорректные данные, попробуйте ещё раз')  # Вы введи неверный id попробуйте ещё раз
    await asyncio.sleep(1)


anketa_dialog = Dialog(
    Window(
        Const('Отправьте мне ваше ФИО'),
        TextInput(
            id='id_input',
            type_factory=fio_check,
            on_success=correct_fio_handler,
            on_error=error_fio_handler,
        ),
        MessageInput(
            func=message_not_text_handler,
            content_types=ContentType.ANY,
        ),
        Cancel(
            Const('◀️'),
            id='cancel'),
        state=ANKETA.fio),

    Window(
        Const(
            '<b>Введите название организации от которой едете, или отправьте <i>"нет"</i>, если участвуете как независимый участник</b>'),
        TextInput(
            id='org_input',
            type_factory=time_check,
            on_success=go_to_3_wind,
            on_error=error_check_time),
        MessageInput(
            func=message_not_text_handler,
            content_types=ContentType.ANY),
        Back(
            Const('◀️'),
            id='back_2'),
        state=ANKETA.org),

    Window(
        Const(
            'Я регистрируюсь для участия в координационной сессии Ассоциации депутатов мирной России 21 декабря в рамках кампании #free120pzk'),
        Row(
            Cancel(text=Const('Нет'),
                   id='sliv_0'),
            Next(Const('Да'),
                 id='bd_0_anketa')),
        state=ANKETA.soglasie),

Window(
    Const('<b>Вы приедите лично или будите участвовать online ?</b>'),
    Back(text=Const('◀️'),
         id='back_3'),
    Group(Row(Button(text=Const('online'),
                     id='online',
                     on_click=online_handler),
              Button(text=Const('Приеду лично'),
                     id='off_line',
                     on_click=offline_handler))),
    state=ANKETA.line),
Window(Const('<b>Вам нужно оплатить дорогу ?</b>'),
       Back(text=Const('◀️'),
            id='back_4'),
       Group(Row(Button(text=Const('Было бы неплохо'),
                        id='yes_pay',
                        on_click=want_way_payment),
                 Button(text=Const('Нет'),
                        id='no_pay',
                        on_click=do_not_want_way_payment))),
       state=ANKETA.roud_expensions),
Window(
    Const('<b>Вам нужно оплатить проживание в отеле ?</b>'),
    Back(text=Const('◀️'),
         id='back_5'),
    Group(Row(
        Button(text=Const('Было бы неплохо'),
               id='yes_pay_hotel',
               on_click=want_hotel_payment),
        Button(text=Const('Нет'),
               id='no_pay_hotel',
               on_click=do_not_want_hotel_payment))),
    state=ANKETA.hotel_expensions),



Window(Const(text='<b>Если Вам нужно оплатить билеты - отправьте, пожалуйста, мне фото ваших билетов</b>'),
       MessageInput(
           func=on_photo_sent,
           content_types=ContentType.PHOTO),
       MessageInput(
           func=message_not_foto_handler,
           content_types=ContentType.ANY),
       Back(text=Const('◀️'),
            id='back_6'),
       Button(text=Const('Нет, не нужно'),
              id='tickets',
              on_click=go_to_arriving_time),
       state=ANKETA.invoice),

Window(
    Const('<b>Анкета заполнена</b>'),
        Button(text=Const('Нажмите ▶️'),
               id='ank_done',
               on_click=anketa_finished),
    state=ANKETA.time_departure)
)

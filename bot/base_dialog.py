from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Group, Row
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
import asyncio
from aiogram_dialog.widgets.input import MessageInput
from anketa_dialog import ANKETA
from bot_instance import START_DIAL, BASE_DIAL
from postgres_functions import return_anketa, return_done, set_selector, insert_done


def code_check(code: str) -> str:
    if code.isdigit() and len(code) == 4:
        return code
    raise ValueError


async def filled_anketa_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    anketa = await return_anketa(event_from_user.id)
    if not anketa:
        anketa = True
    elif len(anketa) > 4:
        anketa = False
    print('anketa = ', anketa)
    done = await return_done(event_from_user.id)
    print('done = ', done)
    getter_data = {'anketa': anketa, 'done': done}
    return getter_data


async def go_to_base_dial(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.start(BASE_DIAL.first)


async def return_to_start(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()


async def go_to_second(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '2')
    await callback.message.answer('Отлично !  🔥')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_third(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    selector = '3'
    await set_selector(callback.from_user.id, selector)
    await callback.message.answer('Здорово !  👍')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_plan(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(msg.from_user.id, '5')
    await msg.answer('Отлично !  🔥')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_zal(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '5')
    await callback.message.answer('Ты молодец !  ✌️')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_session(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '6')
    await callback.message.answer('Хорошо продвигаемся !  😉')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_registr(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '7')
    await callback.message.answer('Замечательно   🤗')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_docs(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '8')
    await callback.message.answer('Замечательно   👍')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def go_to_finish(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '1')
    await callback.message.answer('Супер !  🔥👍')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(BASE_DIAL.first, mode=StartMode.RESET_STACK)  # next()


# async def go_to_sevan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
#                       **kwargs):
#     dialog_manager.dialog_data['selector'] = '1'
#     await callback.message.answer('Молодец ! Регистрируйчя на новые активности ! 🥳')
#     dialog_manager.show_mode = ShowMode.SEND
#     await dialog_manager.done()


async def get_base_1(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    getter_data = {'go': 'Начинаем'}
    return getter_data


async def we_are_waiting(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                         **kwargs):
    await callback.message.answer('Хорошо, мы тебя ждём')
    dialog_manager.show_mode = ShowMode.SEND


async def message_not_text_handler(message: Message, widget: MessageInput,
                                   dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer('Я могу принять только текстовое сообщение')


async def error_code(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                     error: ValueError):
    await message.answer(text='Некорректный код, попробуйте ещё раз')  # Вы введи неверный id попробуйте ещё раз
    await asyncio.sleep(1)


start_dialog = Dialog(Window(
    # Selector = None
    Const('Узнай о новой актвиности'),
    Start(Const('START'),
          id='start',
          state=BASE_DIAL.first),
    state=START_DIAL.start
))

base_dialog = Dialog(
    Window(
        # Selector = None
        Const('Конференция в Берлине\n\nТебе интересно ?', when='anketa'),
        Const('Молодец ! До следующего раза !', when='done'),
        Row(Button(text=Const('Да ну  😞', when='anketa'),
                   id='sliv_second',
                   on_click=return_to_start),
            Button(text=Const('Конечно ! 🤓', when='anketa'),
                   id='go_to_second',
                   on_click=go_to_second)
            ),
        state=BASE_DIAL.first,
        getter=filled_anketa_getter),

    Window(
        # Selector = 2
        Const('Заполните анкету участника'),
        Row(Button(text=Const('Я передумал'),
                   id='sliv_1',
                   on_click=return_to_start),

            Start(text=Const('Хорошо'),
                  id='bd_2_anketa',
                  state=ANKETA.fio)),
        state=BASE_DIAL.second,
    ),
    ############################################################### Selector = 3
    Window(
        # Selector = wait
        Const('<b>Теперь ожидайте сообщения с кодом для дальшейнейшей работы </b>'),
        TextInput(
            id='id_input_code',
            type_factory=code_check,
            on_success=go_to_plan,
            on_error=error_code,
        ),
        MessageInput(
            func=message_not_text_handler,
            content_types=ContentType.ANY, ),
        state=BASE_DIAL.wait
    ),

    Window(
        # Selector = 4
        Const('Нажмите ДА когда получите Адрес Отеля'),
        Group(Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_hotel_adress_else',
                   on_click=we_are_waiting),
            Button(text=Const('Получил'),
                   id='bd_hotel_adress_yes',
                   on_click=go_to_zal),
        )),
        state=BASE_DIAL.hotel_adres,
    ),

    Window(  # Selector = 5
        Const('Нажмите ДА когда получите Номер зала'),
        Group(Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_zal_not_else',
                   on_click=we_are_waiting),
            Button(text=Const('Получил'),
                   id='bd_zal_yes',
                   on_click=go_to_session),
        )),
        state=BASE_DIAL.zal_number,
    ),

    Window(  # Selector = 6
        Const('Нажмите ДА когда получите Программу сессии'),
        Group(Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_6_not_else',
                   on_click=we_are_waiting),
            Button(text=Const('Получил'),
                   id='bd_6_yes',
                   on_click=go_to_registr),
        )),
        state=BASE_DIAL.third,
    ),
    Window(  # Selector = 7
        Const('Нажмите ДА, когда пройдёте Регистрацию'),
        Group(Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_7_not_else',
                   on_click=we_are_waiting),
            Button(text=Const('Прошел Регистрацию'),
                   id='bd_7_yes',
                   on_click=go_to_docs),
        )
        ),
        state=BASE_DIAL.four,
    ),

    Window(  # Selector = 8
        Const('Рабочие документы'),
        Group(Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_8_not_else',
                   on_click=we_are_waiting),

            Button(text=Const('Получил документы'),
                   id='bd_8_yes',
                   on_click=go_to_finish),
        )),

        state=BASE_DIAL.five,
    )

)

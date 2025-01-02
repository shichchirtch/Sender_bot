from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Group, Row
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
import asyncio
from anketa_dialog import ANKETA
from bot_instance import START_DIAL, BASE_DIAL
from postgres_functions import return_anketa, return_done, set_selector, return_selector



async def filled_anketa_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    anketa = await return_anketa(event_from_user.id)
    if not anketa:
        anketa = True
    elif len(anketa) > 4:
        anketa = False
    # print('anketa = ', anketa)
    done = await return_done(event_from_user.id)
    # print('done = ', done)
    getter_data = {'anketa': anketa, 'done': done}
    return getter_data

async def return_to_start(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()


async def go_to_second(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '2')
    await callback.message.answer('Отлично !  🔥')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()

async def go_to_step_hotel(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(message.from_user.id, '4')
    await message.answer('Ожидайте сообщения с адерсом отеля 🙏')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(1)
    await dialog_manager.next()

async def go_to_registr(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    cur_selector = await return_selector(cb.from_user.id)
    if cur_selector == '6s':
        await set_selector(cb.from_user.id, '7')
        await cb.message.answer('Замечательно   🤗')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await cb.message.answer('Дождитесь пожалуйста получения номера зала')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


async def go_to_docs(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await set_selector(callback.from_user.id, '8')
    await callback.message.answer('Замечательно   👍')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()

async def we_are_waiting(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                         **kwargs):
    await callback.message.answer('Хорошо, мы тебя ждём')
    dialog_manager.show_mode = ShowMode.SEND

async def go_next_step(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    cur_selector = await return_selector(cb.from_user.id)
    if cur_selector == '4s':
        await set_selector(cb.from_user.id, '5')
        await cb.message.answer('Отлично !  🔥')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await cb.message.answer('Дождитесь пожалуйста получения адерса отеля')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

async def go_to_zal(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    cur_selector = await return_selector(cb.from_user.id)
    if cur_selector == '5s':
        await set_selector(cb.from_user.id, '6')
        await cb.message.answer('Очень хорошо  🔥')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await cb.message.answer('Дождитесь пожалуйста получения номера зала')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

async def go_to_finish(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    cur_selector = await return_selector(callback.from_user.id)
    if cur_selector == '8s':
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await set_selector(callback.from_user.id, '1')
        await callback.message.answer('Супер !  🔥👍')
        await dialog_manager.start(BASE_DIAL.first, mode=StartMode.RESET_STACK)  # next()
    else:
        await callback.message.answer('Дождитесь пожалуйста получения Рабочих документов')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

########################################################################################################################

start_dialog = Dialog(Window(
    # Selector = None
    Const('Узнай о новой актвиности'),
    Start(Const('START'),
          id='start',
          state=BASE_DIAL.first),
    state=START_DIAL.start
))
########################################################################################################################
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
        # Selector = 4
        Const('Когда получите Адрес Отеля, нажмите ▶️'),
        Row(Button(text=Const('Ещё Нет'),
                   id='bd_hotel_adress_else',
                   on_click=we_are_waiting),
        Button(text=Const('▶️'),
                    id='Hotel_Next',
                   on_click=go_next_step)), # set selector = 5
        state=BASE_DIAL.hotel_adres),
    Window(  # Selector = 5
        Const('Когда получите Номер зала, нажмите ▶️'),
        Row(Button(text=Const('Ещё Нет'),
                   id='bd_zal_not_else',
                   on_click=we_are_waiting),
        Button(text=Const('▶️'),
                    id='Zal_Next',
                   on_click=go_to_zal)), # set selector = 6
        state=BASE_DIAL.zal_number,
    ),

    Window(  # Selector = 6
        Const('Нажмите ▶️ когда получите Программу сессии'),
        Row(Button(text=Const('Ещё Нет'),
                   id='bd_6_not_else',
                   on_click=we_are_waiting),
            Button(text=Const('▶️'),
                   id='bd_6_yes',
                   on_click=go_to_registr),   # set selector = 7
        ),
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
                   on_click=go_to_docs), # set selector = 8
        )
        ),
        state=BASE_DIAL.four,
    ),

    Window(  # Selector = 8
        Const('Нажмите ▶️, когда получите <b>Рабочие документы</b>'),
        Row(
            Button(text=Const('Ещё Нет'),
                   id='bd_8_not_else',
                   on_click=we_are_waiting),

            Button(text=Const('▶️'),
                   id='bd_8_yes',
                   on_click=go_to_finish), # set selector = 1
        ),
        state=BASE_DIAL.five))


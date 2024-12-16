from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from bot_instance import HELP_DIAL



async def help_done(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    print('help_done works')
    await dialog_manager.done()

dialog_help = Dialog(
    Window(
        Const('По всем вопросвам - связь с @ElenaFilina_mundep\n\n'
                'Для получения компенсации обратитесь к @galkinadeputat\n\n🔷'),
        Button(Const('◀️'),
               id='go_to_previous_window',
               on_click=help_done),
        state=HELP_DIAL.erst))


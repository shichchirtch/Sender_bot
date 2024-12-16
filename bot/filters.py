from aiogram.types import Message
from aiogram.filters import BaseFilter






class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id in [6685637602, 419531502, 116486736]:
            return True
        return False








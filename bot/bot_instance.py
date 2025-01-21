from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from config import settings
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import DefaultKeyBuilder

key_builder = DefaultKeyBuilder(with_destiny=True)

using_redis = Redis(host=settings.REDIS_HOST)

redis_storage = RedisStorage(redis=using_redis, key_builder=key_builder)

bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

bot_storage_key = StorageKey(bot_id=bot.id, user_id=bot.id, chat_id=bot.id)

dp = Dispatcher(storage=redis_storage)

class START_DIAL(StatesGroup):
    start = State()

class BASE_DIAL(StatesGroup):
    first = State()
    second = State()
    third = State()
    four = State()
    five = State()
    six = State()
    wait = State()
    post_wait = State()
    hotel_adres = State()
    zal_number = State()

class HELP_DIAL(StatesGroup):
    erst = State()

ban_list = [304463718, 7361946530, 146812561]



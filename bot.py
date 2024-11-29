import random
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

API_TOKEN = '7644429413:AAGNR34gA4L__OsJU5swNAtDyV7udKMoaNQ'

YOUR_CHAT_ID ='-1002380104914'


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Хранение данных о чмонеях
chmoneys = defaultdict(int)
total_members = set()

# Время последнего выбора
last_pick_time = datetime.now()


async def choose_chmoneys():
    global last_pick_time
    while True:
        now = datetime.now()
        if now - last_pick_time >= timedelta(hours=24):
            chat_members = await bot.get_chat_members_count(YOUR_CHAT_ID)
            if chat_members > 0:
                # Случайным образом выбираем пользователя
                user = random.choice(list(total_members))
                chmoneys[user] += 1
                await bot.send_message(YOUR_CHAT_ID, f'{user} чмоней!')
                last_pick_time = now
            await asyncio.sleep(60)  # Ждем 1 минуту, чтобы избежать повторного вызова
        await asyncio.sleep(3600)  # Ждем 1 час перед следующим проверкой


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Я бот, который выбирает чмоней каждый день!")


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    for member in message.new_chat_members:
        total_members.add(member.username)


@dp.message_handler(content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def left_member(message: types.Message):
    if message.left_chat_member.username in total_members:
        total_members.remove(message.left_chat_member.username)


@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    sorted_chmoneys = sorted(chmoneys.items(), key=lambda x: x[1], reverse=True)
    stats_message = "Топ-10 чмоней за текущий год:\n"

    for i, (user, count) in enumerate(sorted_chmoneys[:10], start=1):
        stats_message += f"{i}. {user} — раз(а)\n"

    stats_message += f"\nВсего участников — {len(total_members)}"
    await message.reply(stats_message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(choose_chmoneys())
    executor.start_polling(dp, skip_updates=True)

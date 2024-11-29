import asyncio
import datetime
import random
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from aiogram.utils import executor

# Создать экземпляр бота с хранилищем в памяти
bot = Bot(token="7644429413:AAGNR34gA4L__OsJU5swNAtDyV7udKMoaNQ")
dp = Dispatcher(bot, storage=MemoryStorage())


# Словарь для хранения количества раз, когда каждый пользователь был выбран чмоней
chmonya_counts = {}

# Список всех пользователей, участвующих в игре
participants = set()


@dp.message_handler(Command("start"))
async def start(message: Message):
    participants.add(message.from_user.id)
    await message.answer("Привет! Вы участвуете в игре \"Чмоня дня\".")


@dp.message_handler()
async def handle_message(message: Message):
    if message.from_user.id in participants:
        chmonya_counts[message.from_user.id] = chmonya_counts.get(message.from_user.id, 0) + 1


async def choose_chmonya():
    while True:
        # Выбрать случайного пользователя из списка участников
        chmonya = random.choice(list(participants))

        # Получить количество раз, когда этот пользователь был выбран чмоней
        count = chmonya_counts.get(chmonya, 0)

        # Если пользователь не был выбран чмоней ни разу, выбрать его и отправить сообщение
        if count == 0:
            await bot.send_message(chmonya, "Поздравляем! Вы - чмоня дня!")
            chmonya_counts[chmonya] = 1
        
        # Иначе, увеличить счетчик и подождать 24 часа
        else:
            chmonya_counts[chmonya] += 1
            await asyncio.sleep(86400)  # 24 часа в секундах


# Запустить задачу, которая будет выбирать чмоню дня каждые 24 часа
asyncio.create_task(choose_chmonya())


async def show_stats(message: Message):
    # Получить текущий год
    year = datetime.datetime.now().year

    # Отсортировать словарь по количеству раз, когда каждый пользователь был выбран чмоней
    sorted_chmonya_counts = dict(sorted(chmonya_counts.items(), key=lambda item: item[1], reverse=True))

    # Создать строку со статистикой
    stats = f"Топ-10 чмоней за {year} год:\n\n"
    for i, (user_id, count) in enumerate(sorted_chmonya_counts.items(), start=1):
        user = await bot.get_chat_member(message.chat.id, user_id)
        stats += f"{i}. {user.user.first_name} — {count} раз(а)\n"

    # Отправить статистику пользователю
    await message.answer(stats)


@dp.message_handler(Command("stats"))
async def show_stats(message: Message):
    await show_stats(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

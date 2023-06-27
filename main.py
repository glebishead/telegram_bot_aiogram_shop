import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)


async def on_startup_function(_):
	print("Connection is started...")


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message) -> None:
	await bot.send_message(message.from_id, 'ss')


@dp.message_handler()
async def echo(message: types.Message) -> None:
	await message.reply(message.text)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup_function)


import os
from asyncio import sleep
from json import loads

from aiogram import Bot
from aiogram.types import Message
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


with open('static/messages/messages.json', 'r', encoding='utf-8') as _file:
	messages_text = loads(_file.read())


async def on_startup_function(_) -> None:
	print("----------------------------------", "Connection is started", "Bot is online", sep='\n')


async def bot_typing(message: Message, text: str) -> None:
	await bot.send_chat_action(message.from_id, 'typing')
	await sleep(0.5)
	await bot.send_message(message.from_id, text)


async def bot_sending_sticker(message: Message, sticker_name: str) -> None:
	await bot.send_chat_action(message.from_id, 'choose_sticker')
	await sleep(0.5)
	with open(f'static/stickers/{sticker_name}.tgs', 'rb') as sticker:
		await bot.send_sticker(message.from_id, sticker)


async def bot_sending_photo(message: Message, photo_id: str, caption: [None, str]) -> None:
	await bot.send_chat_action(message.from_id, 'upload_photo')
	await sleep(0.5)
	await bot.send_photo(message.from_id, photo_id, caption=caption)
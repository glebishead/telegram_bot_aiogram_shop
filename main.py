import os
from asyncio import sleep
from json import loads

from aiogram import Bot
from aiogram.types import Message
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


with open('static/messages/messages.json', 'r', encoding='utf-8') as _file:
	messages_text = loads(_file.read())


async def on_startup_function(_) -> None:
	print("----------------------------------", "Connection is started", "Bot is online", sep='\n')


async def bot_typing(message: Message, text: str, **kwargs) -> None:
	await bot.send_chat_action(message.from_id, 'typing')
	await sleep(0.5)
	await bot.send_message(message.from_id, text, **kwargs)


async def bot_sending_sticker(message: Message, sticker_name: str, **kwargs) -> None:
	await bot.send_chat_action(message.from_id, 'choose_sticker')
	await sleep(0.5)
	with open(f'static/stickers/{sticker_name}.tgs', 'rb') as sticker:
		await bot.send_sticker(message.from_id, sticker, **kwargs)


async def bot_sending_photo(message: Message, photo_id: str, **kwargs) -> None:
	await bot.send_chat_action(message.from_id, 'upload_photo')
	await sleep(0.5)
	await bot.send_photo(message.from_id, photo_id, **kwargs)


async def bot_typing_with_callback(callback: CallbackQuery, text: str, **kwargs) -> None:
	await bot.send_chat_action(callback['from']['id'], 'typing')
	await sleep(0.2)
	await bot.send_message(callback['from']['id'], text, **kwargs)


async def bot_sending_photo_with_callback(callback: CallbackQuery, text: str, **kwargs) -> None:
	await bot.send_chat_action(callback['from']['id'], 'upload_photo')
	await sleep(0.2)
	await bot.send_photo(callback['from']['id'], text, **kwargs)


async def bot_answer_callback_query(*args, **kwargs) -> None:
	await bot.answer_callback_query(*args, **kwargs)
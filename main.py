import os
from asyncio import sleep
from typing import Union
from json import loads

from aiogram import Bot
from aiogram.types import Message, MediaGroup
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


with open('static/messages/messages.json', 'r', encoding='utf-8') as _file:
	messages_text = loads(_file.read())


async def on_startup_function(_) -> None:
	print("----------------------------------",
	      "Connection is started",
	      "Bot is online", sep='\n')


async def bot_typing(message: Union[Message, CallbackQuery], text: str, **kwargs) -> None:
	if message.__class__.__name__ == 'Message':
		await bot.send_chat_action(message.from_id, 'typing')
		await sleep(0.2)
		await bot.send_message(message.from_id, text, **kwargs)
	elif message.__class__.__name__ == 'CallbackQuery':
		await bot.send_chat_action(message['from']['id'], 'typing')
		await sleep(0.2)
		await bot.send_message(message['from']['id'], text, **kwargs)


async def bot_sending_sticker(message: Union[Message, CallbackQuery], sticker_name: str, **kwargs) -> None:
	if message.__class__.__name__ == 'Message':
		await bot.send_chat_action(message.from_id, 'choose_sticker')
		await sleep(0.2)
		with open(f'static/stickers/{sticker_name}.tgs', 'rb') as sticker:
			await bot.send_sticker(message.from_id, sticker, **kwargs)
	elif message.__class__.__name__ == 'CallbackQuery':
		await bot.send_chat_action(message['from']['id'], 'choose_sticker')
		await sleep(0.2)
		with open(f'static/stickers/{sticker_name}.tgs', 'rb') as sticker:
			await bot.send_sticker(message['from']['id'], sticker, **kwargs)


async def bot_sending_photo(message: Union[Message, CallbackQuery], photo_id: str, **kwargs) -> None:
	if message.__class__.__name__ == 'Message':
		await bot.send_chat_action(message.from_id, 'upload_photo')
		await sleep(0.2)
		await bot.send_photo(message.from_id, photo_id, **kwargs)
	elif message.__class__.__name__ == 'CallbackQuery':
		await bot.send_chat_action(message.from_id, 'upload_photo')
		await sleep(0.2)
		await bot.send_photo(message['from']['id'], photo_id, **kwargs)
	

async def bot_sending_media(message: Union[Message, CallbackQuery],
                            images: list[str] = None, videos: list[str] = None) -> None:
	media = MediaGroup()
	if images is not None and images != ['']:
		for image in images:
			media.attach_photo(image)
	if videos is not None and videos != ['']:
		for video in videos:
			media.attach_video(video)
			
	if message.__class__.__name__ == 'Message':
		await bot.send_chat_action(message.from_id, 'upload_photo')
		await sleep(0.2)
		await bot.send_media_group(message.from_id, media=media)
	elif message.__class__.__name__ == 'CallbackQuery':
		await bot.send_chat_action(message['from']['id'], 'upload_photo')
		await sleep(0.2)
		await bot.send_media_group(message['from']['id'], media=media)


async def bot_answer_callback_query(callback: CallbackQuery, text: str = None,
                                    show_alert: bool = True, **kwargs) -> None:
	await bot.answer_callback_query(callback.id, text=text, show_alert=show_alert, **kwargs)

import os

from aiogram.types import Message
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text

from main import messages_text, bot_typing, bot_sending_sticker, bot_sending_media
from data import db_session
from data.products import Product
from data.users import User


def register_user_handlers(dp: Dispatcher) -> None:
	dp.register_message_handler(start, commands=['start', 'help'])
	dp.register_message_handler(send_contacts, commands=['contacts'])
	dp.register_message_handler(show_products, commands=['show_products'])
	dp.register_message_handler(passed, Text)


async def start(message: Message) -> None:
	await bot_sending_sticker(message, 'start_sticker')
	await bot_typing(message, messages_text['rus']['command_messages']['start'])
	
	db_sess = db_session.create_session()
	if not db_sess.query(User).filter(User.id == message.from_id).first():
		user = User(id=message.from_id,
		            username=message.chat.username,
		            status='user')
		if message.from_id == int(os.getenv('ADMIN_ID')):
			user.status = 'admin'
		db_sess.add(user)
	db_sess.commit()
	db_sess.close()


async def send_contacts(message: Message) -> None:
	await bot_sending_sticker(message, 'start_sticker')
	await bot_typing(message, messages_text['rus']['command_messages']['telegram_contacts'], parse_mode='HTML')
	await bot_typing(message, messages_text['rus']['command_messages']['avito_contacts'], parse_mode='HTML')
	# with open('text.txt', 'r') as file:
	# 	await bot_typing(message, file.read(), parse_mode='HTML')


async def show_products(message: Message) -> None:
	db_sess = db_session.create_session()
	products = db_sess.query(Product.name, Product.category,
	                         Product.description, Product.images,
	                         Product.videos, Product.price, Product.quantity).all()
	if products:
		for el in products:
			name, category, description, images, videos, price, quantity = el
			images = images.split(' - ')
			videos = videos.split(' - ')
			
			if images != [''] or videos != ['']:
				await bot_sending_media(message, images, videos)
			if quantity.__class__.__name__ == 'int' and quantity > 0:
				await bot_typing(message, f"Название: {name}\nКатегория: {category}\n"
				                          f"Описание: {description}.\nСтоимость {price}₽")
			else:
				await bot_typing(message, f"Название: {name}\nКатегория: {category}\n"
				                          f"Описание: {description}.\nСтоимость {price}₽\n\n"
				                          f"В настоящее время нет в наличии")
	else:
		await bot_typing(message, f"В настоящее время на складе нет товаров")
	db_sess.close()


async def passed(_) -> None:
	print('\nUnresolved command\n')

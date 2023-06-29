import os

from aiogram.types import Message
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text

from main import messages_text, bot_typing, bot_sending_sticker, bot_sending_photo
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
	await bot_typing(message, messages_text['rus']['command_messages']['contacts'])


async def show_products(message: Message) -> None:
	db_sess = db_session.create_session()
	products = db_sess.query(Product.name, Product.description, Product.image, Product.price).all()
	for el in products:
		name, description, image, price = el
		if image not in [None, '']:
			await bot_sending_photo(message, image, caption=f"{name}\n{description}.\n\nСтоимость {price}₽")
		else:
			await bot_typing(message, f"{name}\n{description}.\n\nСтоимость {price}₽")
	db_sess.close()


async def passed(_) -> None:
	print('\nUnresolved command\n')

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
	await bot_typing(message, messages_text['rus']['start'])
	
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
	await bot_typing(message, messages_text['rus']['telegram_contacts'], parse_mode='HTML')
	await bot_typing(message, messages_text['rus']['avito_contacts'], parse_mode='HTML')


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
				await bot_typing(message, messages_text['rus']['show_product'].replace(
					'{name}', f'{name}').replace(
					'{category}', f'{category}').replace(
					'{description}', f'{description}').replace(
					'{price}', f'{price}'))
			else:
				await bot_typing(message, messages_text['rus']['show_product'].replace(
					                 '{name}', f'{name}').replace(
					                 '{category}', f'{category}').replace(
					                 '{description}', f'{description}').replace(
					                 '{price}', f'{price}' +
					                            f"\n\n{messages_text['rus']['fail']['product_not_found']}"))
	else:
		await bot_typing(message, messages_text['rus']['fail']['warehouse_empty'])
	db_sess.close()


async def passed(_) -> None:
	print('\nUnresolved command\n')

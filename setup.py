import os

from aiogram import Bot
from aiogram.types import Message
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor


from asyncio import sleep
from json import loads
from data import db_session
from data.users import User
from data.products import Product


storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


class FSMAdmin(StatesGroup):
	name = State()
	category = State()
	description = State()
	image = State()
	price = State()
	quantity = State()


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
	

async def start(message: Message) -> None:
	await bot_sending_sticker(message, 'start_sticker')
	await bot_typing(message, messages_text['rus']['command_messages']['start'])
	
	db_sess = db_session.create_session()
	if not db_sess.query(User).filter(User.id == message.chat.id).first():
		user = User(id=message.chat.id,
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


async def add_product(message: Message) -> None:
	await FSMAdmin.name.set()
	await bot_typing(message, messages_text['rus']['add_product_states']['name'])


async def add_product_name(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['name'] = message.text
	await FSMAdmin.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['category'])


async def add_product_category(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['category'] = message.text
	await FSMAdmin.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['description'])


async def add_product_description(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['description'] = message.text
	await FSMAdmin.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['image'])


async def add_product_image(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['image'] = message.photo[0].file_id
	await FSMAdmin.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['price'])


async def add_product_price(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['price'] = message.text
	await FSMAdmin.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['quantity'])


async def add_product_quantity(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['quantity'] = message.text
	
	db_sess = db_session.create_session()
	db_sess.add(
		Product(name=data['name'],
		        category=data['category'],
		        description=data['description'],
		        image=data['image'],
		        price=data['price'],
		        quantity=data['quantity']))
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_typing(message, messages_text['rus']['add_product_states']['end'])


async def add_product_cancel(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await state.finish()
	await bot_typing(message, messages_text['rus']['add_product_states']['cancel'])


async def add_product_skip(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	
	cur_state = await state.get_state()
	async with state.proxy() as data:
		data[cur_state[9:]] = ''
	await FSMAdmin.next()
	
	cur_state = await state.get_state()
	if cur_state is None:
		await bot_typing(message, messages_text['rus']['add_product_states']['end'])
		async with state.proxy() as data:
			db_sess = db_session.create_session()
			db_sess.add(
				Product(name=data['name'],
				        category=data['category'],
				        description=data['description'],
				        image=data['image'],
				        price=data['price'],
				        quantity=data['quantity']))
		db_sess.commit()
		db_sess.close()
	else:
		await bot_typing(message, messages_text['rus']['add_product_states'][cur_state[9:]])


if __name__ == '__main__':
	try:
		db_session.global_init('db/shop.db')
		
		dp.register_message_handler(start, commands=['start', 'help'])
		dp.register_message_handler(send_contacts, commands=['contacts'])
		dp.register_message_handler(show_products, commands=['show_products'])
		
		dp.register_message_handler(add_product, commands=['add_product'])
		dp.register_message_handler(add_product_cancel, commands=['cancel'], state='*')
		dp.register_message_handler(add_product_skip, commands=['skip'], state='*')
		dp.register_message_handler(add_product_name, state=FSMAdmin.name)
		dp.register_message_handler(add_product_category, state=FSMAdmin.category)
		dp.register_message_handler(add_product_description, state=FSMAdmin.description)
		dp.register_message_handler(add_product_image, content_types=['photo'], state=FSMAdmin.image)
		dp.register_message_handler(add_product_price, state=FSMAdmin.price)
		dp.register_message_handler(add_product_quantity, state=FSMAdmin.quantity)
		
		executor.start_polling(dp, skip_updates=True, on_startup=on_startup_function)
	except Exception as e:
		print(e)


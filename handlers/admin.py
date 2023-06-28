from aiogram.types import Message
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

from main import bot_typing, messages_text
from data import db_session
from data.users import User
from data.products import Product


def register_admin_handlers(dp: Dispatcher) -> None:
	dp.register_message_handler(add_product, commands=['add_product'])
	dp.register_message_handler(add_product_cancel, commands=['cancel'], state='*')
	dp.register_message_handler(add_product_skip, commands=['skip'], state='*')
	dp.register_message_handler(add_product_name, state=FSMAdmin.name)
	dp.register_message_handler(add_product_category, state=FSMAdmin.category)
	dp.register_message_handler(add_product_description, state=FSMAdmin.description)
	dp.register_message_handler(add_product_image, content_types=['photo'], state=FSMAdmin.image)
	dp.register_message_handler(add_product_price, state=FSMAdmin.price)
	dp.register_message_handler(add_product_quantity, state=FSMAdmin.quantity)


class FSMAdmin(StatesGroup):
	name = State()
	category = State()
	description = State()
	image = State()
	price = State()
	quantity = State()


async def add_product(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		await FSMAdmin.name.set()
		await bot_typing(message, messages_text['rus']['add_product_states']['name'])
	db_sess.close()


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

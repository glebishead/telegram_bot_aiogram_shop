import pprint

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

from main import messages_text, bot_typing, bot_sending_photo, \
	bot_answer_callback_query, bot_typing_with_callback, bot_sending_photo_with_callback
from data import db_session
from data.users import User
from data.products import Product


def register_admin_handlers(dp: Dispatcher) -> None:
	dp.register_message_handler(add_product, commands=['add_product'])
	
	dp.register_message_handler(add_product_cancel, commands=['cancel'], state=AddProductStates.states)
	dp.register_message_handler(add_product_skip, commands=['skip'], state='*')
	
	dp.register_message_handler(add_product_name, state=AddProductStates.name)
	dp.register_message_handler(add_product_category, state=AddProductStates.category)
	dp.register_message_handler(add_product_description, state=AddProductStates.description)
	dp.register_message_handler(add_product_image, content_types=['photo'], state=AddProductStates.image)
	dp.register_message_handler(add_product_price, state=AddProductStates.price)
	dp.register_message_handler(add_product_quantity, state=AddProductStates.quantity)
	
	dp.register_message_handler(choose_product, commands=['edit_products'])
	dp.register_message_handler(edit_product_cancel, commands=['cancel'], state=EditProductStates.states)
	dp.register_callback_query_handler(choose_product_info, state=EditProductStates.product_info)
	dp.register_callback_query_handler(enter_new_info, state=EditProductStates.new_info)
	dp.register_message_handler(edit_product_finish, content_types=['photo', 'text'], state=EditProductStates.edit_product)


class AddProductStates(StatesGroup):
	name = State()
	category = State()
	description = State()
	image = State()
	price = State()
	quantity = State()


class EditProductStates(StatesGroup):
	product_info = State()
	new_info = State()
	edit_product = State()


async def add_product(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		await AddProductStates.name.set()
		await bot_typing(message, messages_text['rus']['add_product_states']['name'])
	db_sess.close()


async def add_product_name(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['name'] = message.text
	await AddProductStates.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['category'])


async def add_product_category(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['category'] = message.text
	await AddProductStates.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['description'])


async def add_product_description(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['description'] = message.text
	await AddProductStates.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['image'])


async def add_product_image(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['image'] = message.photo[0].file_id
	await AddProductStates.next()
	await bot_typing(message, messages_text['rus']['add_product_states']['price'])


async def add_product_price(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['price'] = message.text
	await AddProductStates.next()
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
		data[cur_state.replace('AddProductStates:', '')] = ''
	await AddProductStates.next()
	
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
		await bot_typing(message, messages_text['rus']['add_product_states'][cur_state.replace('AddProductStates:', '')])


async def choose_product(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		products = db_sess.query(Product.id, Product.name, Product.description, Product.image, Product.price).all()
		
		for el in products:
			product_id, name, description, image, price = el
			if image not in [None, '']:
				await bot_sending_photo(message, image, caption=f"Название: {name}\n"
				                        f"Описание: {description}\n"
				                        f"Цена: {price}₽\n",
				                        reply_markup=InlineKeyboardMarkup(one_time_keyboard=True).add(
					                        InlineKeyboardButton('Изменить', callback_data=f'edit_{product_id}')))
			else:
				await bot_typing(message, f"Название: {name}\n"
				                 f"Описание: {description}\n"
				                 f"Цена: {price}₽\n",
				                 reply_markup=InlineKeyboardMarkup(one_time_keyboard=True).add(
					                    InlineKeyboardButton('Изменить', callback_data=f'edit_{product_id}')))
			
		await EditProductStates.product_info.set()
	db_sess.close()


async def choose_product_info(callback: CallbackQuery, state=FSMContext):
	async with state.proxy() as _data:
		_data['product_id'] = int(callback.data.replace('edit_', ''))
	
	db_sess = db_session.create_session()
	product = db_sess.query(Product.name, Product.category,
	                        Product.description, Product.image,
	                        Product.price, Product.quantity).filter(Product.id == _data['product_id']).first()
	
	name, category, description, image, price, quantity = product
	
	markup = InlineKeyboardMarkup(one_time_keyboard=True).add(
		InlineKeyboardButton('изменить название', callback_data=f'name')).add(
		InlineKeyboardButton('изменить категорию', callback_data=f'category')).add(
		InlineKeyboardButton('изменить описание', callback_data=f'description')).add(
		InlineKeyboardButton('изменить изображение', callback_data=f'image')).add(
		InlineKeyboardButton('изменить цену', callback_data=f'price')).add(
		InlineKeyboardButton('изменить количество', callback_data=f'quantity'))
	
	if image not in [None, '']:
		await bot_sending_photo_with_callback(callback, image, caption=f"Название: {name}\n"
		                                                               f"Категория: {category}\n"
		                                                               f"Описание: {description}\n"
		                                                               f"Цена: {price}₽\n"
		                                                               f"Количество: {quantity}\n",
		                                      reply_markup=markup)
	else:
		await bot_typing_with_callback(callback, f"Название: {name}\n"
		                                         f"Категория: {category}\n"
		                                         f"Описание: {description}\n"
		                                         f"Цена: {price}₽\n"
		                                         f"Количество: {quantity}\n",
		                               reply_markup=markup)
	
	await EditProductStates.next()
	db_sess.close()


async def enter_new_info(callback: CallbackQuery, state=FSMContext):
	async with state.proxy() as _data:
		_data['info_type'] = callback.data
	await bot_typing_with_callback(callback, {'name': 'Введите новое название товара',
	                                          'category': 'Введите новую категорию товара',
	                                          'description': 'Введите новое описание товара',
	                                          'image': 'Прикрепите новое изображение товара',
	                                          'price': 'Введите новую цену товара',
	                                          'quantity': 'Введите новое количество товара'}[_data['info_type']])
	await EditProductStates.next()


async def edit_product_finish(message: Message, state=FSMContext):
	async with state.proxy() as _data:
		if _data['info_type'] != 'image':
			_data['new_info'] = message.text
		else:
			_data['new_info'] = message.photo[0].file_id
	
	db_sess = db_session.create_session()
	product = db_sess.query(Product).filter(Product.id == _data['product_id']).first()
	match _data['info_type']:
		case 'name':
			product.name = _data['new_info']
		case 'category':
			product.category = _data['new_info']
		case 'description':
			product.description = _data['new_info']
		case 'image':
			product.image = _data['new_info']
		case 'price':
			product.price = _data['new_info']
		case 'quantity':
			product.quantity = _data['new_info']
	
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_typing(message, messages_text['rus']['success']['edit_product'])


async def edit_product_cancel(callback: CallbackQuery, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await state.finish()
	await bot_typing_with_callback(callback, messages_text['rus']['fail']['edit_product_cancel'])

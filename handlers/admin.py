from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters import MediaGroupFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_media_group import media_group_handler


from main import messages_text, bot_typing, bot_sending_media, bot_answer_callback_query
from data import db_session
from data.users import User
from data.products import Product


def register_admin_handlers(dp: Dispatcher) -> None:
	dp.register_message_handler(add_product, commands=['add_product'])
	
	dp.register_message_handler(add_product_cancel, commands=['cancel'], state=AddProductStates.states)
	dp.register_message_handler(add_product_skip, commands=['skip'], state=AddProductStates.states)
	
	dp.register_message_handler(add_product_name, state=AddProductStates.name)
	dp.register_message_handler(add_product_category, state=AddProductStates.category)
	dp.register_message_handler(add_product_description, state=AddProductStates.description)
	dp.register_message_handler(add_product_media_group, MediaGroupFilter(is_media_group=True),
	                            content_types=['photo', 'video'], state=AddProductStates.media)
	dp.register_message_handler(add_product_media, content_types=['photo', 'video'], state=AddProductStates.media)
	dp.register_message_handler(add_product_price, state=AddProductStates.price)
	dp.register_message_handler(add_product_quantity, state=AddProductStates.quantity)
	
	dp.register_message_handler(choose_product, commands=['edit_products'])
	dp.register_message_handler(edit_product_cancel, commands=['cancel'], state=EditProductStates.states)
	dp.register_callback_query_handler(choose_product_info, state=EditProductStates.product_info)
	dp.register_callback_query_handler(enter_new_info, state=EditProductStates.new_info)
	dp.register_message_handler(edit_product_finish_with_text, content_types=['text'],
	                            state=EditProductStates.edit_product)
	dp.register_message_handler(edit_product_finish_with_media_group, MediaGroupFilter(is_media_group=True),
	                            content_types=['photo', 'video'], state=EditProductStates.edit_product)
	dp.register_message_handler(edit_product_finish_with_media, content_types=['photo', 'video'],
	                            state=EditProductStates.edit_product)
	
	dp.register_message_handler(edit_status, commands=['edit_status'])
	dp.register_message_handler(edit_status_cancel, commands=['cancel'], state=EditStatusStates.states)
	dp.register_message_handler(choose_status, state=EditStatusStates.user_id)
	dp.register_callback_query_handler(edit_status_end, state=EditStatusStates.new_status)
	
	dp.register_message_handler(show_everybody_start, commands=['show_everyone'])
	dp.register_message_handler(show_everybody_cancel, commands=['cancel'], state=ShowEveryoneStates.show)
	dp.register_message_handler(show_everybody_end, content_types=['photo', 'video', 'sticker', 'text'],
	                            state=ShowEveryoneStates.show)


class AddProductStates(StatesGroup):
	name = State()
	category = State()
	description = State()
	media = State()
	price = State()
	quantity = State()


class EditProductStates(StatesGroup):
	product_info = State()
	new_info = State()
	edit_product = State()


class EditStatusStates(StatesGroup):
	user_id = State()
	new_status = State()


class ShowEveryoneStates(StatesGroup):
	show = State()


async def add_product(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		await bot_typing(message, messages_text['rus']['add_product']['name'])
		await AddProductStates.name.set()
	db_sess.close()


async def add_product_name(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['name'] = message.text
	await bot_typing(message, messages_text['rus']['add_product']['category'])
	await AddProductStates.next()


async def add_product_category(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['category'] = message.text
	await bot_typing(message, messages_text['rus']['add_product']['description'])
	await AddProductStates.next()


async def add_product_description(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['description'] = message.text
	await bot_typing(message, messages_text['rus']['add_product']['media'])
	await AddProductStates.next()


@media_group_handler
async def add_product_media_group(messages: list[Message], state=FSMContext) -> None:
	async with state.proxy() as data:
		for message in messages:
			if 'images' not in data.keys() and message.photo:
				data['images'] = [message.photo[-1].file_id]
			elif 'videos' not in data.keys() and message.video:
				data['videos'] = [message.video['file_id']]
			elif 'images' in data.keys() and message.photo:
				data['images'].append(message.photo[-1].file_id)
			elif 'videos' in data.keys() and message.video:
				data['videos'].append(message.video['file_id'])
	await bot_typing(message, messages_text['rus']['add_product']['price'])
	await AddProductStates.next()


async def add_product_media(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		if message.photo:
			data['images'] = [message.photo[-1].file_id]
		elif message.video:
			data['videos'] = [message.video['file_id']]
	await bot_typing(message, messages_text['rus']['add_product']['price'])
	await AddProductStates.next()


async def add_product_price(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['price'] = int(message.text)
	await bot_typing(message, messages_text['rus']['add_product']['quantity'])
	await AddProductStates.next()


async def add_product_quantity(message: Message, state=FSMContext) -> None:
	async with state.proxy() as data:
		data['quantity'] = message.text
		if 'images' not in data.keys():
			data['images'] = ''
		if 'videos' not in data.keys():
			data['videos'] = ''
	db_sess = db_session.create_session()
	db_sess.add(
		Product(name=data['name'],
		        category=data['category'],
		        description=data['description'],
		        images=' - '.join(data['images']),
		        videos=' - '.join(data['videos']),
		        price=data['price'],
		        quantity=data['quantity']))
	db_sess.commit()
	db_sess.close()
	
	await bot_typing(message, messages_text['rus']['add_product']['end'])
	await state.finish()


async def add_product_cancel(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await bot_typing(message, messages_text['rus']['add_product']['cancel'])
	await state.finish()


async def add_product_skip(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	
	cur_state = await state.get_state()
	async with state.proxy() as data:
		data[cur_state.replace('AddProductStates:', '')] = ''
	await AddProductStates.next()
	
	cur_state = await state.get_state()
	if cur_state is None:
		await bot_typing(message, messages_text['rus']['add_product']['end'])
		async with state.proxy() as data:
			if 'images' not in data.keys():
				data['images'] = ''
			if 'videos' not in data.keys():
				data['videos'] = ''
				
			db_sess = db_session.create_session()
			db_sess.add(
				Product(name=data['name'],
				        category=data['category'],
				        description=data['description'],
				        images=' - '.join(data['images']),
				        videos=' - '.join(data['videos']),
				        price=data['price'],
				        quantity=data['quantity']))
		db_sess.commit()
		db_sess.close()
	else:
		await bot_typing(message, messages_text['rus']['add_product'][cur_state.replace('AddProductStates:', '')])


async def choose_product(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		products = db_sess.query(Product.id, Product.name, Product.category,
		                         Product.description, Product.images,
		                         Product.videos, Product.price).all()
		for el in products:
			product_id, name, category, description, images, videos, price = el
			images = images.split(' - ')
			videos = videos.split(' - ')
			
			if images != [''] or videos != ['']:
				await bot_sending_media(message, images, videos)
			await bot_typing(message, messages_text['rus']['show_product'].replace(
				'{name}', f'{name}').replace(
				'{category}', f'{category}').replace(
				'{description}', f'{description}').replace(
				'{price}', f'{price}'),
			                 reply_markup=InlineKeyboardMarkup(one_time_keyboard=True).add(
					                    InlineKeyboardButton(messages_text['rus']['change'], callback_data=f'edit_{product_id}')).add(
					                    InlineKeyboardButton(messages_text['rus']['delete'], callback_data=f'delete_{product_id}')))
		await EditProductStates.product_info.set()
	db_sess.close()


async def choose_product_info(callback: CallbackQuery, state=FSMContext):
	db_sess = db_session.create_session()
	if callback.data.startswith('delete_'):
		product_id = int(callback.data.replace('delete_', ''))
		product = db_sess.query(Product).filter(Product.id == product_id).first()
		db_sess.delete(product)
		
		db_sess.commit()
		db_sess.close()
		await state.finish()
		await bot_answer_callback_query(callback, messages_text['rus']['edit_product']['delete'])
	else:
		async with state.proxy() as _data:
			_data['product_id'] = int(callback.data.replace('edit_', ''))
		
		
		product = db_sess.query(Product.name, Product.category,
		                        Product.description, Product.images, Product.videos,
		                        Product.price, Product.quantity).filter(Product.id == _data['product_id']).first()
		
		name, category, description, images, videos, price, quantity = product
		
		markup = InlineKeyboardMarkup(one_time_keyboard=True).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['name'], callback_data=f'name')).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['category'], callback_data=f'category')).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['description'], callback_data=f'description')).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['media'], callback_data=f'media')).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['price'], callback_data=f'price')).add(
			InlineKeyboardButton(messages_text['rus']['edit_product']['quantity'], callback_data=f'quantity'))
	
		images = images.split(' - ')
		videos = videos.split(' - ')
		
		if images != [''] or videos != ['']:
			await bot_sending_media(callback, images, videos)
		await bot_typing(callback, messages_text['rus']['show_product'].replace(
				'{name}', f'{name}').replace(
				'{category}', f'{category}').replace(
				'{description}', f'{description}').replace(
				'{price}', f'{price}'), reply_markup=markup)
		
		await EditProductStates.next()
		db_sess.close()


async def enter_new_info(callback: CallbackQuery, state=FSMContext):
	async with state.proxy() as _data:
		_data['info_type'] = callback.data
	await bot_typing(callback, messages_text['rus']['edit_product']['enter'][_data['info_type']])
	await EditProductStates.next()


async def edit_product_finish_with_text(message: Message, state=FSMContext):
	async with state.proxy() as _data:
		_data['new_info'] = message.text
	
	db_sess = db_session.create_session()
	product = db_sess.query(Product).filter(Product.id == _data['product_id']).first()
	match _data['info_type']:
		case 'name':
			product.name = _data['new_info']
		case 'category':
			product.category = _data['new_info']
		case 'description':
			product.description = _data['new_info']
		case 'price':
			product.price = _data['new_info']
		case 'quantity':
			product.quantity = _data['new_info']
	
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_typing(message, messages_text['rus']['edit_product']['end'])


@media_group_handler
async def edit_product_finish_with_media_group(messages: list[Message], state=FSMContext):
	async with state.proxy() as _data:
		_data['new_info'] = {}
		for message in messages:
			if 'images' not in _data['new_info'].keys() and message.photo:
				_data['new_info']['images'] = [message.photo[-1].file_id]
			elif 'videos' not in _data['new_info'].keys() and message.video:
				_data['new_info']['videos'] = [message.video['file_id']]
			elif 'images' in _data['new_info'].keys() and message.photo:
				_data['new_info']['images'].append(message.photo[-1].file_id)
			elif 'videos' in _data['new_info'].keys() and message.video:
				_data['new_info']['videos'].append(message.video['file_id'])
	
	if 'videos' not in _data['new_info'].keys():
		_data['new_info']['videos'] = ''
	if 'images' not in _data['new_info'].keys():
		_data['new_info']['images'] = ''
	db_sess = db_session.create_session()
	product = db_sess.query(Product).filter(Product.id == _data['product_id']).first()
	product.images = ' - '.join(_data['new_info']['images'])
	product.videos = ' - '.join(_data['new_info']['videos'])
	
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_typing(messages[-1], messages_text['rus']['edit_product']['end'])


async def edit_product_finish_with_media(message: Message, state=FSMContext):
	async with state.proxy() as _data:
		db_sess = db_session.create_session()
		product = db_sess.query(Product).filter(Product.id == _data['product_id']).first()
		if message.photo:
			product.images = message.photo[-1].file_id
			product.videos = ''
		elif message.video:
			product.images = ''
			product.videos = message.video['file_id']
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_typing(message, messages_text['rus']['edit_product']['end'])


async def edit_product_cancel(callback: CallbackQuery, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await state.finish()
	await bot_typing(callback, messages_text['rus']['edit_product']['cancel'])


async def edit_status(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		await bot_typing(message, messages_text['rus']['edit_status']['start'])
		await EditStatusStates.user_id.set()
	db_sess.close()


async def choose_status(message: Message, state=FSMContext) -> None:
	db_sess = db_session.create_session()
	try:
		async with state.proxy() as _data:
			_data['id'] = int(message.text)
		if db_sess.query(User).filter(User.id == _data['id']).first() is None:
			await bot_typing(message, messages_text['rus']['fail']['id_not_found'])
			await bot_typing(message, messages_text['rus']['edit_status']['start'])
		else:
			await bot_typing(message, messages_text['rus']['edit_status']['enter_status'],
			                 reply_markup=InlineKeyboardMarkup(one_time_keyboard=True).add(
				InlineKeyboardButton('user', callback_data=f'user')).add(
				InlineKeyboardButton('seller', callback_data=f'seller')).add(
				InlineKeyboardButton('owner', callback_data=f'owner')).add(
				InlineKeyboardButton('admin', callback_data=f'admin')))
			await EditStatusStates.next()
	except ValueError:
		await bot_typing(message, messages_text['rus']['edit_status']['start'])
	db_sess.close()


async def edit_status_end(callback: CallbackQuery, state=FSMContext):
	async with state.proxy() as _data:
		_data['status'] = callback.data
		
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == _data['id']).first()
	person.status = _data['status']
	db_sess.commit()
	db_sess.close()
	
	await state.finish()
	await bot_answer_callback_query(callback, messages_text['rus']['edit_status']['end'])


async def edit_status_cancel(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await bot_typing(message, messages_text['rus']['edit_status']['cancel'])
	await state.finish()
	
	
async def show_everybody_start(message: Message) -> None:
	db_sess = db_session.create_session()
	person = db_sess.query(User).filter(User.id == message.from_id).first()
	if person.status not in ('admin', 'owner'):
		await bot_typing(message, messages_text['rus']['fail']['low_status'])
	else:
		await bot_typing(message, messages_text['rus']['show_everyone']['start'])
		await ShowEveryoneStates.show.set()
	db_sess.close()


async def show_everybody_end(message: Message, state=FSMContext) -> None:
	db_sess = db_session.create_session()
	persons = db_sess.query(User).all()
	for person in persons:
		await message.copy_to(person.id)
	await bot_typing(message, messages_text['rus']['show_everyone']['end'])
	await state.finish()


async def show_everybody_cancel(message: Message, state=FSMContext) -> None:
	if await state.get_state() is None:
		return
	await bot_typing(message, messages_text['rus']['show_everyone']['cancel'])
	await state.finish()

from aiogram.utils import executor

from data import db_session
from main import dp, on_startup_function
from handlers.admin import register_admin_handlers
from handlers.user import register_user_handlers


if __name__ == '__main__':
	try:
		db_session.global_init('db/shop.db')
		
		register_admin_handlers(dp)
		register_user_handlers(dp)
		
		executor.start_polling(dp, skip_updates=True, on_startup=on_startup_function)
	except Exception as e:
		print(e)


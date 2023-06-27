from sqlalchemy import Column, Integer, String
from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    name = Column(String)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=True)

    def remove_product(self):
        self.quantity -= 1

    def add_product(self):
        self.quantity += 1
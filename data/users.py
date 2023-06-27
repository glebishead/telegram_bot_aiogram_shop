from sqlalchemy import Column, String, Integer
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String)
    status = Column(String)

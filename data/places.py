import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Places(SqlAlchemyBase):
    __tablename__ = 'Places'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    deprecation_full = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    opening_hours = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link_map =sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_photo_main = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_photo_1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_photo_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    open_hour = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    close_hour = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
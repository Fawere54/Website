import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

ReviewsBase = declarative_base()


class Review(ReviewsBase):
    __tablename__ = 'reviews'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.String, nullable=False)
    rating = sa.Column(sa.Integer, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.now)
    user_id = sa.Column(sa.Integer, nullable=False)
    user_name = sa.Column(sa.String, nullable=False)
    place_id = sa.Column(sa.Integer, nullable=False)

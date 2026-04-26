import sqlalchemy as sa
import sqlalchemy.orm as orm
from .reviews import ReviewsBase

__factory_reviews = None


def global_init_reviews(db_file):
    global __factory_reviews
    if __factory_reviews:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных отзывов.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    engine = sa.create_engine(conn_str, echo=False)
    __factory_reviews = orm.sessionmaker(bind=engine)
    ReviewsBase.metadata.create_all(engine)


def create_reviews_session():
    global __factory_reviews
    return __factory_reviews()

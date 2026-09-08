from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)


def get_db():
    """Функция для иньекции сессии Базы Данных"""
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

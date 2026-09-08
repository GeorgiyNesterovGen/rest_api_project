from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.services.categories_services import CategoriesService
from app.services.task_services import TaskService


def get_task_service(db: Session = Depends(get_db)):
    """Функция для иньекции зависимости"""
    return TaskService(db)


def get_category_service(db: Session = Depends(get_db)):
    """Функция для иньекции зависимости категорий"""
    return CategoriesService(db)

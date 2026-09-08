from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categories_models import CategoriesORM


class CategoriesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> Sequence[CategoriesORM]:
        return self.db.scalars(select(CategoriesORM)).all()

    def get_by_id(self, categories_id: str) -> CategoriesORM | None:
        return self.db.get(CategoriesORM, categories_id)

    def create(self, name: str) -> CategoriesORM:
        new_categories = CategoriesORM(name=name)
        self.db.add(new_categories)
        return new_categories

    def delete(self, category: CategoriesORM) -> None:
        self.db.delete(category)

    # Тут все сделал

    # ОСталось сделать рефакторинг и добавление все в сервисе
    # Проверить схемы категорий
    # И настроить роуты категорий

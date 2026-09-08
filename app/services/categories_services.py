from sqlalchemy.orm import Session

from app.repositories.categories_repositories import CategoriesRepository
from app.schemas.categories_schemas import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)


class CategoryNotFound(Exception):
    """Категория не найдена в БД"""


class CategoriesService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.categories_repository = CategoriesRepository(db)

    def lists_categories(self):
        categories_orm = self.categories_repository.get_all()
        return [CategorySchema.model_validate(category) for category in categories_orm]

    def create_category(self, category_create: CategoryCreateSchema) -> CategorySchema:
        category_orm = self.categories_repository.create(name=category_create.name)
        self.db.commit()
        return CategorySchema.model_validate(category_orm)

    def update_category(
        self, category_id: str, category_update: CategoryUpdateSchema
    ) -> CategorySchema:

        category_orm = self.categories_repository.get_by_id(categories_id=category_id)
        if category_orm is None:
            raise CategoryNotFound(f"Категория с id {category_id} не найдена")

        if category_update.name is not None:
            category_orm.name = category_update.name

        self.db.commit()
        return CategorySchema.model_validate(category_orm)

    def category_delete(self, category_id: str) -> None:

        category_orm = self.categories_repository.get_by_id(category_id)
        if category_orm is None:
            raise CategoryNotFound(f"Категория с id {category_id} не найдена")

        self.categories_repository.delete(category=category_orm)
        self.db.commit()

from unittest.mock import Mock

import pytest

from app.models.categories_models import CategoriesORM
from app.schemas.categories_schemas import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from app.services.categories_services import CategoriesService, CategoryNotFound


def test_list_category_returns_pydantic_models(
    category_service: CategoriesService, category_repository_mock: Mock
) -> None:

    # Aragge подготовка данных моков
    # Имитируем что метод get_all категорий вернет эти задачи орм моделями
    category_repository_mock.get_all.return_value = [
        CategoriesORM(id="category-1", name="Jopen"),
        CategoriesORM(id="category-2", name="Uchim_tests"),
    ]

    # Вызываем метод поулчается у реального сервиса

    result = category_service.lists_categories()

    assert result == [
        CategorySchema(id="category-1", name="Jopen"),
        CategorySchema(id="category-2", name="Uchim_tests"),
    ]


def test_create_category_commits_created(
    category_repository_mock, category_service, db_mock
):

    # arrage

    category_repository_mock.create.return_value = CategorySchema(
        id="категория-1",
        name="new категория",
    )

    result = category_service.create_category(
        CategoryCreateSchema(name="new категория")
    )

    category_repository_mock.create.assert_called_once_with(name="new категория")
    db_mock.commit.assert_called_once()

    assert result.model_dump() == {
        "id": "категория-1",
        "name": "new категория",
    }


@pytest.mark.parametrize(
    ("payload", "expected_name"),
    [
        pytest.param(
            CategoryUpdateSchema(name="Новая категория"),
            "Новая категория",
        ),
        pytest.param(CategoryUpdateSchema(name=None), "Стараая атегоиря"),
    ],
)
def test_update_category_updates_only_passed_fields(
    category_service: CategoriesService,
    category_repository_mock: Mock,
    db_mock: Mock,
    payload: CategoryUpdateSchema,
    expected_name: str,
) -> None:

    # Arrage podgortovka настраиваем мок гвоорим какие данные ему вернуть
    # при получение
    # апдейта
    category_orm = CategoriesORM(id="category-1", name="Стараая атегоиря")

    category_repository_mock.get_by_id.return_value = category_orm

    result = category_service.update_category("category-1", payload)
    db_mock.commit.assert_called_once()

    assert result.model_dump() == {"id": "category-1", "name": expected_name}


def test_update_category_raises_when_task_not_found(
    category_repository_mock: Mock,
    db_mock: Mock,
    category_service: CategoriesService,
):

    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFound):
        category_service.update_category(
            "missing-categoru", CategoryUpdateSchema(name="Похуй ваще")
        )

    db_mock.commit.assert_not_called()


def test_category_delete(
    category_repository_mock: Mock,
    db_mock: Mock,
    category_service: CategoriesService,
):

    category_orm = CategoriesORM(id="category-1", name="xuy")
    category_repository_mock.get_by_id.return_value = category_orm

    category_service.category_delete(category_id="category-1")
    category_repository_mock.delete.assert_called_once_with(category=category_orm)
    category_repository_mock.get_by_id.assert_called_once_with("category-1")
    db_mock.commit.assert_called_once()


def test_category_delete_raise(
    category_repository_mock: Mock,
    db_mock: Mock,
    category_service: CategoriesService,
):

    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFound):
        category_service.category_delete("poxuy")

    db_mock.commit.assert_not_called()

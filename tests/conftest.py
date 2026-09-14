from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.repositories.categories_repositories import CategoriesRepository
from app.repositories.tasks_repositories import TaskRepository
from app.services.categories_services import CategoriesService
from app.services.task_services import TaskService


@pytest.fixture
def db_mock() -> Mock:
    """Создаем мок сессии БД один раз и переиспользуем в тестах"""
    return Mock(spec=Session)


@pytest.fixture
def repository_mock() -> Mock:
    """Создаем мок TaskRepository один раз и переисползуем в тестах"""
    return Mock(spec=TaskRepository)


@pytest.fixture
def service(db_mock: Mock, repository_mock: Mock) -> TaskService:
    """Создаем TaskService один раз, чтобы переисопльзовать в тестах"""
    task_service = TaskService(db_mock)
    task_service.task_repository = repository_mock
    return task_service


@pytest.fixture
def category_repository_mock() -> Mock:
    """Создаем мок TaskRepository один раз и переисползуем в тестах"""
    return Mock(spec=CategoriesRepository)


@pytest.fixture
def category_service(
    db_mock: Mock, category_repository_mock: Mock
) -> CategoriesService:
    """Создаем CategoryService один раз, чтобы переисопльзовать в тестах"""
    categor_service = CategoriesService(db_mock)
    categor_service.categories_repository = category_repository_mock
    return categor_service

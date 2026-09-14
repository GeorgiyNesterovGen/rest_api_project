from unittest.mock import Mock

import pytest

from app.models.task_models import TaskORM
from app.schemas.task_schemas import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task_services import TaskNotFound, TaskService


def test_list_tasks_returns_pydantic_models(
    service: TaskService,
    repository_mock: Mock,
) -> None:
    # Этап 1 ARRANGE ПОДГОТОВКА ДАННЫХ
    # Имитируем что метод get_all репозитория вернет эти задачи
    repository_mock.get_all.return_value = [
        TaskORM(id="task-1", title="Изучить Pytest", completed=False),
        TaskORM(
            id="task-2",
            title="Написать первый тест",
            completed=True,
        ),
    ]

    # ЭТАП 2 Дейсвтие Лоигка теста
    result = service.list_tasks()

    # Assert проверка тум мы првоерем результат он должен совпадать
    assert result == [
        TaskSchema(id="task-1", title="Изучить Pytest", completed=False),
        TaskSchema(id="task-2", title="Написать первый тест", completed=True),
    ]


def test_create_task_commits_created_task(
    service: TaskService, db_mock: Mock, repository_mock: Mock
) -> None:
    # Тестовые данные
    created_task = TaskORM(
        id="task-1", title="Тестируем создание задачи", completed=False
    )

    # Настраиваем мок отдаем тестовые данные которые должен будет нам отдать
    repository_mock.create.return_value = created_task

    # Вызываем метод сервиса то есть передаем как будто запрос на создание задачи

    result = service.create_task(TaskCreateSchema(title="Тестируем создание задачи"))

    # 4 Тестируем что запрос попал в фейк базу поулчается? Проверяем результат

    repository_mock.create.assert_called_once_with(title="Тестируем создание задачи")
    db_mock.commit.assert_called_once_with()

    assert result.model_dump() == {
        "id": "task-1",
        "title": "Тестируем создание задачи",
        "completed": False,
    }


# Тут мы создаем параметризованный тест черезе декоратор из пайтеста
# Данный тест прогоняется 3 раза для каждого элемента в списке параметризе
@pytest.mark.parametrize(
    # После мы сразу вкидываем данные
    ("payload", "expected_title", "expected_completed"),
    [
        pytest.param(
            TaskUpdateSchema(title="Обновить заголовок"),  # payload
            "Обновить заголовок",  # expected_title
            False,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(completed=True),  # payload
            "Старая задача",  # expected_title
            True,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(title="Готовая задача", completed=True),
            "Готовая задача",
            True,
        ),
    ],
)
def test_update_task_updates_only_passed_fields(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool,
) -> None:

    # Настраиваем мок говорим ему какие данные вернуть при получение апдейта?
    task = TaskORM(id="task-1", title="Старая задача", completed=False)
    repository_mock.get_by_id.return_value = task

    # Само тестирование
    result = service.update_task("task-1", payload)

    # Проверка что метод внутри сервиса вызвался хоть 1 раз с ID == task-1
    # Проверка что коммит был выполнен хоть 1 раз
    repository_mock.get_by_id.assert_called_once_with(task_id="task-1")
    db_mock.commit.assert_called_once_with()

    # Ожидаеый результат после теста они должны совпадать с данными которые мы даем.
    assert result.model_dump() == {
        "id": "task-1",
        "title": expected_title,
        "completed": expected_completed,
    }


# Добавляем тест со сценарием TaskNotFound


def test_update_task_raises_when_task_not_found(
    service: TaskService,
    repository_mock: Mock,
    db_mock: Mock,
) -> None:
    # Нужно натсроить мок на данных - присваем что база
    # якобы вернет NOne по запросу
    # get_by_id
    repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFound):  # Должна произайти указанная ошибка
        service.update_task("missing_task", TaskUpdateSchema(title="Неважно"))
    # Проверяем что коммит не был вызван ни разу --
    # т.к задачи то нет такой ее н получилось
    # бы получить мы бы хотели иметь None
    db_mock.commit.assert_not_called()

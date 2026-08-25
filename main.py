from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, Session


DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    
    
class TaskORM(Base):
    __tablename__ = "tasks"
    
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


class CategoriesORM(Base):
    __tablename__ = "categories"
    
    name: Mapped[str]

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class BookSchema(BaseModel):
    book: str
    
    
class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None
    
    
class CategorySchema(BaseModel):
    id : str
    name: str


class CategoryCreateSchema(BaseModel):
    name: str
    
    
class CategoryUpdateSchema(BaseModel):
    name: str | None


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)


def categories_orm_to_model(categories_orm: CategoriesORM) -> CategorySchema:
    return CategorySchema(id = categories_orm.id, name = categories_orm.name)


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    task_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in task_from_db]


@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    
    return task_orm_to_model(new_task)


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    task_for_update = db.get(TaskORM,task_id)
    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
        task_for_update.completed = payload.completed
        
    db.commit()
    return task_orm_to_model(task_for_update)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleted_task(task_id, db:Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()
    

@app.patch("/categories/{category_id}", status_code=status.HTTP_200_OK)
def update_categories(category_id: str, payload: CategoryUpdateSchema, db: Session = Depends(get_db)) -> CategorySchema:
    
    categories_for_update = db.get(CategoriesORM, category_id) 
    if not categories_for_update:
        raise HTTPException(404,"Категория не найдена")
    if payload.name is not None:
        categories_for_update.name = payload.name
    
    db.commit()
    return categories_orm_to_model(categories_for_update)
    

@app.get("/categories", status_code=status.HTTP_200_OK)
def read_categories(db: Session= Depends(get_db)) -> list[CategorySchema]:
    
    categories_from_db = db.scalars(select(CategoriesORM)).all()
    
    return [categories_orm_to_model(categor) for categor in categories_from_db]
    

@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_categories(payload: CategoryCreateSchema, db: Session = Depends(get_db)) -> CategorySchema:
    new_categories = CategoriesORM(name=payload.name)
    
    db.add(new_categories)
    db.commit()
    
    return categories_orm_to_model(new_categories)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def categories_deleted(category_id: str, db: Session = Depends(get_db)) -> None:
    
    categories_for_delete = db.get(CategoriesORM, category_id)
    
    if not categories_for_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category is not found")
    db.delete(categories_for_delete)
    db.commit()
        
    
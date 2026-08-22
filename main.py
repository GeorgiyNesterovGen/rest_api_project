from uuid import uuid4
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

tasks: list[TaskSchema] = []
books = []
categories = []

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
    id: str | None
    name: str | None


@app.patch("/categories/{category_id}", status_code=status.HTTP_200_OK)
def update_categories(category_id: str, payload: CategoryUpdateSchema):
    for category in categories:
        if category is not None:
            if category.id == category_id:
                category.name = payload.name
            return category
    




@app.get("/categories", status_code=status.HTTP_200_OK)
def read_categories() -> list[CategorySchema]:
    return categories



@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_categories(payload: CategoryCreateSchema):
    new_categories = CategorySchema(id=str(uuid4()), name=payload.name)
    categories.append(new_categories)
    return new_categories


    
@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks



@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema) -> TaskSchema:
    new_task = TaskSchema(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(new_task)
    return new_task


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title
            if payload.completed is not None:    
                task.completed = payload.completed
            return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleted_task(task_id):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)



@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def categories_deleted(category_id: str):
    
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category is not found")


@app.post("/book")
def add_book(payload:BookSchema):

    books.append(payload.book)
    return payload

@app.get("/book")
def read_book():
    return f" Любимая книга {books[-1]}" if books else "Книг пока нет"
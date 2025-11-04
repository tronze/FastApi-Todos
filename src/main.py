import json
import os
import time
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()

# Jinja Template Loading을 위한 초기화.
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# Static file serving
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


class TodoItem(BaseModel):
    title: str
    description: str


# To-Do 항목 모델
class TodoItemOut(TodoItem):
    id: int
    completed: bool


# JSON 파일 경로 (환경변수 TODO_FILE로 오버라이드 가능)
TODO_FILE = os.environ.get("TODO_FILE", os.path.join(BASE_DIR, "todo.json"))


# JSON 파일에서 To-Do 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            return sorted(
                json.load(file),
                key=lambda x: (x["completed"], -x["id"])
            )
    return []


# JSON 파일에 To-Do 항목 저장
def save_todos(todos):
    # 상위 디렉터리가 없으면 생성 (예: TODO_FILE=/data/todo.json)
    os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4)


# TodoList Main Page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    todos: list[TodoItemOut] = load_todos()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"todos": todos}
    )


# 신규 To-Do 항목 추가
@app.post("/", response_class=RedirectResponse)
def create_todo(todo: Annotated[TodoItem, Form()]):
    data = todo.model_dump()
    data['id'] = int(time.time())
    data['completed'] = False
    todos = load_todos()
    todos.append(data)
    save_todos(todos)
    redirect_url = app.url_path_for("read_root")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# To-Do 항목 수정
@app.post("/edit", response_class=RedirectResponse)
def update_todo(updated_todo: Annotated[TodoItemOut, Form()]):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == updated_todo.id:
            todo.update(updated_todo.model_dump())
            save_todos(todos)
    redirect_url = app.url_path_for("read_root")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# To-Do 항목 삭제
@app.post("/delete", response_class=RedirectResponse)
def delete_todo(todo_id: Annotated[int, Form()]):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    redirect_url = app.url_path_for("read_root")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

from bs4 import BeautifulSoup

import pytest
import os
from fastapi.testclient import TestClient
from main import app, save_todos, TodoItemOut, load_todos

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전 초기화
    save_todos([])
    yield
    # 테스트 후 정리
    save_todos([])


def test_load_todos_returns_empty_when_file_missing(tmp_path, monkeypatch):
    # main.TODO_FILE을 존재하지 않는 임시 경로로 변경
    missing_file = tmp_path / "todo.json"
    monkeypatch.setattr("main.TODO_FILE", str(missing_file), raising=False)

    # 파일이 실제로 존재하지 않음을 보장
    assert not os.path.exists(missing_file)

    # 이제 load_todos는 존재하지 않는 파일 경로를 보게 되어 빈 리스트를 반환해야 함
    assert load_todos() == []


def test_get_todos_empty():
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    assert len(children) == 0


def test_get_todos_with_items():
    todos = [
        TodoItemOut(id=1, title="Test", description="Test description", completed=False),
        TodoItemOut(id=2, title="Test", description="Test description", completed=True)
    ]
    save_todos([todo.model_dump() for todo in todos])
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    assert len(children) == 2
    assert children[0].h5.text == "Test"
    assert children[0].p.text == "Test description"
    assert "list-group-item-success" not in children[0]["class"]
    assert children[1].h5.text == "Test"
    assert children[1].p.text == "Test description"
    assert "list-group-item-success" in children[1]["class"]


def test_create_todo():
    todo = {"title": "Test Creation", "description": "Test description"}
    response = client.post("/", data=todo)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    created = None
    for child in children:
        if child.h5.text == "Test Creation":
            created = child
    assert created is not None
    assert created.p.text == "Test description"
    assert "list-group-item-success" not in created["class"]


def test_create_todo_invalid():
    todo = {"id": 1, "title": "Test"}
    response = client.post("/", data=todo)
    assert response.status_code == 422


def test_update_todo():
    todos = [
        TodoItemOut(id=1, title="Test", description="Test description", completed=False),
        TodoItemOut(id=2, title="Test", description="Test description", completed=True)
    ]
    save_todos([todo.model_dump() for todo in todos])
    updated_todo = {"id": 1, "title": "Test Updated", "description": "Test description", "completed": "True"}
    response = client.post("/edit", data=updated_todo)
    assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    updated = None
    for child in children:
        if child.small.text == "ID : 1":
            updated = child
    assert updated is not None
    assert updated.h5.text == "Test Updated"
    assert updated.p.text == "Test description"
    assert "list-group-item-success" in updated["class"]


def test_update_todo_not_found():
    updated_todo = {"id": 3, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.post("/edit", data=updated_todo)
    assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    assert len(children) == 0


def test_delete_todo():
    todos = [
        TodoItemOut(id=1, title="Test", description="Test description", completed=False),
        TodoItemOut(id=2, title="Test", description="Test description", completed=True)
    ]
    save_todos([todo.model_dump() for todo in todos])
    response = client.post("/delete", data={"todo_id": "1"})
    assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    assert len(children) == 1
    left = None
    for child in children:
        if child.small.text == "ID : 2":
            left = child
    assert left is not None
    assert left.h5.text == "Test"
    assert left.p.text == "Test description"
    assert "list-group-item-success" in left["class"]


def test_delete_todo_not_found():
    todos = [
        TodoItemOut(id=1, title="Test", description="Test description", completed=False),
        TodoItemOut(id=2, title="Test", description="Test description", completed=True)
    ]
    save_todos([todo.model_dump() for todo in todos])
    response = client.post("/delete", data={"todo_id": "3"})
    assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    children = list(soup.find("div", id="todo-list").find_all("div", class_="list-group-item"))
    assert len(children) == 2


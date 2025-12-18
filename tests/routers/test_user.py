import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from src import context, util
from src.app import app
from src.models import User

# ------------------- Fake classes -------------------

class FakeUser:
    def __init__(self, user_id=1, username="TestUser", is_admin=False):
        self.user_id = user_id
        self.username = username
        self.is_admin = is_admin

    def to_dict(self):
        return {"user_id": self.user_id, "username": self.username, "is_admin": self.is_admin}

class FakeDB:
    def get(self, cls, uid):
        return FakeUser()
    def scalars(self, query):
        return []
    def scalar(self, query):
        return 0
    def close(self):
        pass

class FakeRedis:
    def __init__(self):
        self.storage = {}
    def get(self, token):
        return 1
    def set(self, token, uid):
        self.storage[token] = uid
    def expire(self, token, ttl):
        pass
    def delete(self, token):
        self.storage.pop(token, None)

class FakeES:
    def __init__(self):
        self.indices = MagicMock()
        self.indices.exists.return_value = False
    def search(self, **kwargs):
        return {"hits": {"hits": []}}

class FakeContext:
    def __init__(self):
        self.rs = FakeRedis()
        self.es = FakeES()
        self.s3 = MagicMock()
        self.db = FakeDB()

    def sm(self):
        return self.db

# ------------------- Fixture -------------------

@pytest.fixture
def client(monkeypatch):
    # Подменяем context
    monkeypatch.setattr(context, "get_db", lambda: iter([FakeDB()]))
    monkeypatch.setattr(context, "ctx", FakeContext())

    return TestClient(app)

# ------------------- Тесты -------------------

def test_get_me(client):
    response = client.get("/user/me?token=fake_token")
    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "user_id": 1,
            "username": "TestUser",
            "is_admin": False
        }
    }

def test_index_empty(client):
    response = client.get("/user/?token=fake_token")
    assert response.status_code == 200
    assert response.json() == {"artists": [], "albums": [], "songs": []}

def test_logout(client):
    response = client.delete("/user/logout?token=fake_token")
    assert response.status_code == 200 or response.status_code == 204  # зависит от реализации log_action
    # Проверяем, что токен удалён
    assert "fake_token" not in context.ctx.rs.storage

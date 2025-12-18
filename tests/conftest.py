import pytest
from fastapi.testclient import TestClient
from src.app import app
from src import context, util


# ------------------ Fake Classes ------------------

class FakeRedis:
    def __init__(self):
        self.storage = {}

    def exists(self, key):
        return key in self.storage

    def set(self, key, value):
        self.storage[key] = value

    def expire(self, key, ttl):
        pass


class FakeUser:
    def __init__(self, user_id=1, username='test', password='hashed', is_admin=False):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.is_admin = is_admin


class FakeDB:
    def __init__(self):
        self.users = {}

    def scalar(self, query):
        # query будет искать по username
        # для простоты возвращаем единственного пользователя
        if self.users:
            return next(iter(self.users.values()))
        return None

    def add(self, obj):
        self.users[obj.username] = obj

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, obj):
        obj.user_id = 1

    def close(self):
        pass


# ------------------ Fake Context ------------------

class FakeContext:
    def __init__(self):
        self.rs = FakeRedis()
        self.db = FakeDB()

    def sm(self):
        return self.db


# ------------------ Pytest Fixture ------------------

@pytest.fixture
def client(monkeypatch):
    fake_db = FakeDB()
    fake_ctx = FakeContext()

    # Подмена context.get_db и context.ctx
    def fake_get_db():
        yield fake_db

    monkeypatch.setattr(context, 'get_db', fake_get_db)
    monkeypatch.setattr(context, 'ctx', fake_ctx)

    return TestClient(app)

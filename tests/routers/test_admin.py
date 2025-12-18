import pytest
from fastapi.testclient import TestClient
from src.routers import admin
from src import context, util

# ------------------ Fake Classes ------------------

class FakeRedis:
    def __init__(self):
        self.storage = {}
    def get(self, key):
        return self.storage.get(key)
    def set(self, key, value):
        self.storage[key] = value
    def expire(self, key, ttl):
        pass

class FakeUser:
    def __init__(self, user_id=1, username='admin', password='hash', is_admin=True):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.is_admin = is_admin
    def to_dict(self):
        return {"user_id": self.user_id, "username": self.username, "is_admin": self.is_admin}

class FakeDB:
    def __init__(self):
        self.users = {1: FakeUser()}
    def get(self, cls, uid):
        return self.users.get(uid)
    def add(self, obj):
        self.users[obj.user_id] = obj
    def commit(self):
        pass
    def rollback(self):
        pass
    def refresh(self, obj):
        pass
    def delete(self, obj):
        self.users.pop(obj.user_id, None)
    def scalar(self, query):
        return len(self.users)
    def scalars(self, query):
        return list(self.users.values())
    def close(self):
        pass


class FakeContext:
    def __init__(self):
        self.rs = FakeRedis()
        self.rs.storage['token'] = 1  # admin user
        self.s3 = type('FakeS3', (), {
            'head_bucket': lambda self, Bucket: None,
            'create_bucket': lambda self, Bucket: None,
            'put_object': lambda self, Bucket, Key, Body, ContentType: None
        })()
        self.db = FakeDB()

    def sm(self):
        return self.db

# ------------------ Fixture ------------------

@pytest.fixture
def client(monkeypatch):
    fake_db = FakeDB()
    fake_ctx = FakeContext()

    # Подменяем context
    monkeypatch.setattr(context, 'get_db', lambda: iter([fake_db]))
    monkeypatch.setattr(context, 'ctx', fake_ctx)

    # Подменяем util
    monkeypatch.setattr(util, 'hashpw', lambda p: f'hash-{p}')
    monkeypatch.setattr(util, 'checkpw', lambda p, h: h == f'hash-{p}')
    monkeypatch.setattr(util, 'generate_token', lambda: 'token')

    # Подменяем логгер
    monkeypatch.setattr(admin, 'log_action', lambda *a, **kw: None)

    from src.app import app
    return TestClient(app)

# ------------------ Тесты ------------------

def test_users_list(client):
    resp = client.get("/admin/users?token=token")
    assert resp.status_code == 200
    data = resp.json()
    assert 'total' in data
    assert 'items' in data
    assert len(data['items']) >= 1

def test_users_create(client):
    resp = client.post("/admin/users?token=token", json={
        "username": "newuser",
        "password": "1234",
        "is_admin": False
    })
    assert resp.status_code == 200
    user = resp.json()['user']
    assert user['username'] == 'newuser'

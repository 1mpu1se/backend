import pytest
from src.models.user import User
from src import const

# ------------------ Фикстуры ------------------

@pytest.fixture
def fake_user():
    u = User()
    u.user_id = 1
    u.username = "TestUser"
    u.password = b"secret"
    u.is_admin = False
    return u

# ------------------ Тесты ------------------

def test_to_dict(fake_user):
    d = fake_user.to_dict()
    assert d['user_id'] == 1
    assert d['username'] == "TestUser"
    assert d['is_admin'] is False

def test_username_set_validation():
    user = User()
    # Короткое имя
    with pytest.raises(ValueError):
        user.username = "a"
    # Длинное имя
    with pytest.raises(ValueError):
        user.username = "a" * 1000
    # Корректное имя
    user.username = "ValidUser"
    assert user.username == "ValidUser"

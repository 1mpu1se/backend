import pytest
from fastapi import HTTPException
from src.routers.__base__ import assert_exists


# ------------------ Fake DB ------------------
class FakeDB:
    def __init__(self, data=None, raise_exc=False):
        self.data = data or {}
        self.raise_exc = raise_exc

    def get(self, cls, uid):
        if self.raise_exc:
            raise ValueError("Some error")
        return self.data.get(uid)


# ------------------ Tests ------------------
def test_assert_exists_returns_object():
    db = FakeDB(data={1: {"id": 1, "name": "test"}})
    result = assert_exists(db, dict, 1)
    assert result == {"id": 1, "name": "test"}


def test_assert_exists_none_raises_404():
    db = FakeDB(data={})
    with pytest.raises(HTTPException) as excinfo:
        assert_exists(db, dict, 1)
    assert excinfo.value.status_code == 404


def test_assert_exists_exception_raises_404():
    db = FakeDB(raise_exc=True)
    with pytest.raises(HTTPException) as excinfo:
        assert_exists(db, dict, 1)
    assert excinfo.value.status_code == 404

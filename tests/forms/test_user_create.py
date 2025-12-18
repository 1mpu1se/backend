import pytest
from pydantic import ValidationError
from src.forms.user_create import UserCreateForm
from src import const

def test_user_create_form_valid():
    form = UserCreateForm(
        username="validuser",
        password="validpassword",
        is_admin=True
    )
    assert form.username == "validuser"
    assert form.password == "validpassword"
    assert form.is_admin is True

def test_user_create_form_invalid_username():
    # слишком короткий username
    with pytest.raises(ValidationError):
        UserCreateForm(
            username="a",
            password="validpassword",
            is_admin=False
        )
    # слишком длинный username
    with pytest.raises(ValidationError):
        UserCreateForm(
            username="a" * (const.USER_USERNAME_LENGTH[1] + 1),
            password="validpassword",
            is_admin=False
        )

def test_user_create_form_invalid_password():
    # слишком короткий password
    with pytest.raises(ValidationError):
        UserCreateForm(
            username="validuser",
            password="123",
            is_admin=False
        )
    # слишком длинный password
    with pytest.raises(ValidationError):
        UserCreateForm(
            username="validuser",
            password="a" * (const.USER_PASSWORD_LENGTH[1] + 1),
            is_admin=False
        )

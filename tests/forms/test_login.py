import pytest
from pydantic import ValidationError
from src.forms.login import LoginForm
from src import const

def test_login_form_valid():
    form = LoginForm(
        username="validuser",
        password="validpassword"
    )
    assert form.username == "validuser"
    assert form.password == "validpassword"

def test_login_form_username_too_short():
    with pytest.raises(ValidationError):
        LoginForm(
            username="a",  # слишком короткое имя
            password="validpassword"
        )

def test_login_form_username_too_long():
    with pytest.raises(ValidationError):
        LoginForm(
            username="a" * (const.USER_USERNAME_LENGTH[1] + 1),  # слишком длинное имя
            password="validpassword"
        )

def test_login_form_password_too_short():
    with pytest.raises(ValidationError):
        LoginForm(
            username="validuser",
            password="a" * (const.USER_PASSWORD_LENGTH[0] - 1)  # слишком короткий пароль
        )

def test_login_form_password_too_long():
    with pytest.raises(ValidationError):
        LoginForm(
            username="validuser",
            password="a" * (const.USER_PASSWORD_LENGTH[1] + 1)  # слишком длинный пароль
        )

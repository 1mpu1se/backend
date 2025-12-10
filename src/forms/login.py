from pydantic import BaseModel, Field

import const


class LoginForm(BaseModel):
    username: str = Field(title='Имя пользователя', min_length=const.USER_USERNAME_LENGTH[0],
                          max_length=const.USER_USERNAME_LENGTH[1])
    password: str = Field(title='Пароль', min_length=const.USER_PASSWORD_LENGTH[0],
                          max_length=const.USER_PASSWORD_LENGTH[1])

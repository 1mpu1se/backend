from pydantic import BaseModel, Field

import src.const as const


class UserCreateForm(BaseModel):
    username: str = Field(title='Имя пользователя', min_length=const.USER_USERNAME_LENGTH[0],
                          max_length=const.USER_USERNAME_LENGTH[1])
    password: str = Field(title='Пароль', min_length=const.USER_PASSWORD_LENGTH[0],
                          max_length=const.USER_PASSWORD_LENGTH[1])
    is_admin: bool = Field(title='Является ли администратором')

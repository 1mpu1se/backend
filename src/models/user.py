from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column

import src.const as const
from src.models.__base__ import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    is_admin: Mapped[bool] = mapped_column(default=False)

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'is_admin': self.is_admin
        }


@event.listens_for(User.username, 'set')
def username_set(target, value, oldvalue, initiator):
    length = len(value)
    if length < const.USER_USERNAME_LENGTH[0] or length > const.USER_USERNAME_LENGTH[1]:
        raise ValueError(f'User username must be between {const.USER_USERNAME_LENGTH} characters long')

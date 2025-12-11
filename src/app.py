from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

import config
import const
import context
import util
from forms import LoginForm
from logger import log_user_action as log_action
from models import User
from routers import (
    user_router,
    admin_router
)

"""
APP
"""

app = FastAPI(title='1mpu1se backend', version='1.0.0b')

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins(),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

"""
HELPERS
"""


def generate_token(user: User) -> str:
    redis = context.ctx.rs

    limit = 100
    while True:
        limit -= 1
        token = util.generate_token()
        if not redis.exists(token):
            break
        if limit == 0:
            raise HTTPException(500)

    redis.set(token, user.user_id)
    redis.expire(token, const.SESSION_TTL)

    return token


"""
ENDPOINTS
"""


@app.get('/',
         name='Индекс',
         description="""
Используется для проверки работоспособности системы.

---

Успешный ответ:
```
{
    "version": "<версия_api>"    
}
```

""")
async def index():
    return {
        'version': app.version
    }


@app.post('/login',
          name='Логин',
          description="""
Форма логина в систему.

---

Тело запроса:
```
{
    "username": "<имя_пользователя>",
    "password": "<пароль>"
}
```

---

Успешный ответ:
```
{
    "token": "<токен_сессии>"
}
```

""")
async def login(form: LoginForm):
    db = next(context.get_db())

    user = db.scalar(select(User).where(User.username == form.username))
    if user is None or not util.checkpw(form.password, user.password):
        raise HTTPException(401)

    log_action(user.user_id, 'login')

    return {'token': generate_token(user)}


@app.post('/register',
          name='Регистрация',
          description="""
Форма регистрации в системе.
Первый зарегистрированный пользователь становится администратором.

---

Тело запроса:
```
{
    "username": "<имя_пользователя>",
    "password": "<пароль>"
}
```

---

Успешный ответ:
```
{
    "token": "<токен_сессии>"
}
```

""")
async def register(form: LoginForm):
    db = next(context.get_db())

    count = db.scalar(select(func.count()).select_from(User))

    user = User(
        username=form.username,
        password=util.hashpw(form.password),
        is_admin=(count == 0)
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(user.user_id, 'register')

    return {'token': generate_token(user)}


"""
ROUTERS
"""

app.include_router(user_router)
app.include_router(admin_router)

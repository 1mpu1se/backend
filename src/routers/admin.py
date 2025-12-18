from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Depends
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

import const
import context
import util
from forms import (
    AlbumForm,
    ArtistForm,
    SongForm,
    UserCreateForm,
    UserUpdateForm
)
from logger import log_admin_action as log_action
from models import (
    Asset,
    User,
    Artist,
    Song,
    Album,
)
from routers.__base__ import assert_exists

"""
ROUTER
"""

router = APIRouter(prefix='/admin', tags=['admin'])

"""
HELPERS
"""


def assert_is_admin(db: Session, token: str) -> User:
    redis = context.ctx.rs

    user_id = redis.get(token)
    if user_id is None:
        raise HTTPException(404)

    user = db.get(User, int(user_id))
    if user is None or not user.is_admin:
        raise HTTPException(404)

    redis.set(token, user.user_id)
    redis.expire(token, const.SESSION_TTL)

    return user


"""
USERS
"""


@router.get('/users',
            name='Список',
            description="""
Список пользователей.

---

Параметры запроса:
- token - токен сессии
- page - номер страницы

---

Успешный ответ:
```
{
  "total": <всего_записей>,
  "page": <текущая_страница>,
  "per_page": <записей_на_страницу>,
  "items": [
    <записи>
  ]
}
```

            """)
async def users_list(
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(User))
        users = db.scalars(
            select(User).offset(const.ELEMENTS_PER_PAGE * (page - 1)).limit(const.ELEMENTS_PER_PAGE).order_by(
                User.user_id))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in users]
    }


@router.post('/users',
             name='Создание',
             description="""
Создает нового пользователя.

---

Параметры запроса:
- token - токен сессии

Тело запроса:
```
{
    "username": "<имя_пользователя>",
    "password": "<пароль>",
    "is_admin": <является_ли_администратором - true/false>
}
```

Имя пользователя должно быть уникальным.

---

Успешный ответ - объект пользователя:
```
{
  "user": {
    "user_id": <id_пользователя>,
    "username": "<имя>",
    "is_admin": <является_ли_администратором - true/false>
  }
}
```

            """)
async def users_create(
    token: Annotated[str, Query(title='Токен сессии')],
    body: UserCreateForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    try:
        user = User(username=body.username, password=util.hashpw(body.password), is_admin=body.is_admin)

        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'user_create', {
        'user': str(user.to_dict())
    })

    return {
        'user': user.to_dict()
    }


@router.get('/users/{user_id}',
            name='Информация',
            description="""
Информация о пользователе.

---

Параметры запроса:
- user_id - ID пользователя
- token - токен сессии

---

Успешный ответ - объект пользователя:
```
{
  "user": {
    "user_id": <id_пользователя>,
    "username": "<имя>",
    "is_admin": <является_ли_администратором - true/false>
  }
}
```

            """)
async def users_read(
    user_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    return {
        'user': assert_exists(db, User, user_id).to_dict()
    }


@router.put('/users/{user_id}',
            name='Изменение',
            description="""
Изменение пользователя.
Администратор, выполняющий действие, не может забрать у себя права администратора.

---

Параметры запроса:
- user_id - ID пользователя
- token - токен сессии

Тело запроса:
```
{
    "username": "<имя_пользователя>",
    "password": "<пароль>",
    "is_admin": <является_ли_администратором - true/false>
}
```

Если не нужно изменять пароль, то поле "password" можно не использовать.

---

Успешный ответ - объект пользователя после изменений:
```
{
  "user": {
    "user_id": <id_пользователя>,
    "username": "<имя>",
    "is_admin": <является_ли_администратором - true/false>
  }
}
```

            """)
async def users_update(
    user_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    body: UserUpdateForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)
    user = assert_exists(db, User, user_id)

    if me.user_id == user.user_id and body.is_admin == False:
        raise HTTPException(400)

    try:
        user.username = body.username
        user.is_admin = body.is_admin

        if body.password is not None:
            user.password = util.hashpw(body.password)

        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'user_update', {
        'user': str(user.to_dict())
    })

    return {
        'user': user.to_dict()
    }


@router.delete('/users/{user_id}',
               name='Удаление',
               description="""
Удаление пользователя.
Администратор, выполняющий действие, не может быть удален.

---

Тело запроса:
- user_id - ID пользователя
- token - токен сессии

---

Успешный ответ - объект пользователя до удаления:
```
{
  "user": {
    "user_id": <id_пользователя>,
    "username": "<имя>",
    "is_admin": <является_ли_администратором - true/false>
  }
}
```

            """)
async def users_delete(
    user_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)
    user = assert_exists(db, User, user_id)

    if me.user_id == user.user_id:
        raise HTTPException(400)

    try:
        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'users_delete', {
        'user': str(user.to_dict())
    })

    return {
        'user': user.to_dict()
    }


"""
ARTISTS
"""


@router.get('/artists',
            name='Список',
            description="""
Список исполнителей.

---

Параметры запроса:
- token - токен сессии
- page - номер страницы

---

Успешный ответ:
```
{
  "total": <всего_записей>,
  "page": <текущая_страница>,
  "per_page": <записей_на_страницу>,
  "items": [
    <записи>
  ]
}
```

            """)
async def artists_list(
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(Artist))
        artists = db.scalars(
            select(Artist).offset(const.ELEMENTS_PER_PAGE * (page - 1)).limit(const.ELEMENTS_PER_PAGE).order_by(
                Artist.artist_id))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in artists]
    }


@router.post('/artists',
             name='Создание',
             description="""
Создание нового исполнителя.

---

Параметры запроса:
- token - токен сессии

Тело запроса:
```
{
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id" <id_вложения_обложки>
}
```

Имя исполнителя должно быть уникальным.

---

Успешный ответ - объект исполнителя:
```
{
  "artist": {
    "artist_id": <id_исполнителя>,
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def artists_create(
    token: Annotated[str, Query(title='Токен сессии')],
    body: ArtistForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    try:
        artist = Artist(name=body.name, biography=body.biography, asset_id=body.asset_id)

        db.add(artist)
        db.commit()
        db.refresh(artist)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'artist_create', {
        'artist': str(artist.to_dict())
    })

    return {
        'artist': artist.to_dict()
    }


@router.get('/artists/{artist_id}',
            name='Информация',
            description="""
Информация об исполнителе.

---

Параметры запроса:
- artist_id - ID исполнителя
- token - токен сессии

---

Успешный ответ - объект исполнителя:
```
{
  "artist": {
    "artist_id": <id_исполнителя>,
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def artists_read(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    return {
        'artist': assert_exists(db, Artist, artist_id).to_dict()
    }


@router.put('/artists/{artist_id}',
            name='Изменение',
            description="""
Изменение исполнителя.

---

Параметры запроса:
- artist_id - ID исполнителя
- token - токен сессии

Тело запроса:
```
{
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id" <id_вложения_обложки>
}
```

---

Успешный ответ - объект исполнителя после изменений:
```
{
  "artist": {
    "artist_id": <id_исполнителя>,
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def artists_update(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    body: ArtistForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    artist = assert_exists(db, Artist, artist_id)

    try:
        artist.name = body.name
        artist.biography = body.biography
        artist.asset_id = body.asset_id

        db.commit()
        db.refresh(artist)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'artist_update', {
        'artist': str(artist.to_dict())
    })

    return {
        'artist': artist.to_dict()
    }


@router.delete('/artists/{artist_id}',
               name='Удаление',
               description="""
Удаление исполнителя.

---

Параметры запроса:
- artist_id - ID исполнителя
- token - токен сессии

---

Успешный ответ - объект исполнителя до удаления:
```
{
  "artist": {
    "artist_id": <id_исполнителя>,
    "name": "<имя>",
    "biography": "<биография>",
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def artists_delete(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    artist = assert_exists(db, Artist, artist_id)

    try:
        db.delete(artist)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'artist_delete', {
        'artist': str(artist.to_dict())
    })

    return {
        'artist': artist.to_dict()
    }


@router.get('/artists/{artist_id}/albums',
            name='Список',
            description="""
Список альбомов исполнителя.

---

Параметры запроса:
- artist_id - ID исполнителя
- token - токен сессии
- page - номер страницы

---

Успешный ответ:
```
{
  "total": <всего_записей>,
  "page": <текущая_страница>,
  "per_page": <записей_на_страницу>,
  "items": [
    <записи>
  ]
}
```


            """)
async def artists_albums(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(Album).where(Album.artist_id == artist_id))
        albums = db.scalars(
            select(Album).where(Album.artist_id == artist_id).offset(const.ELEMENTS_PER_PAGE * (page - 1)).limit(
                const.ELEMENTS_PER_PAGE).order_by(
                Album.album_id))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in albums]
    }


"""
ALBUMS
"""


@router.post('/albums',
             name='Создание',
             description="""
Создание нового альбома.

---

Параметры запроса:
- token - токен сессии

Тело запроса:
```
{
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
}
```

---

Успешный ответ - объект альбома:
```
{
  "album": {
    "album_id": <id_альбома>,
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def albums_create(
    token: Annotated[str, Query(title='Токен сессии')],
    body: AlbumForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    try:
        album = Album(name=body.name, artist_id=body.artist_id, asset_id=body.asset_id)

        db.add(album)
        db.commit()
        db.refresh(album)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'album_create', {
        'album': str(album.to_dict())
    })

    return {
        'album': album.to_dict()
    }


@router.get('/albums/{album_id}',
            name='Информация',
            description="""
Информация об альбоме.

---

Параметры запроса:
- album_id - ID альбома
- token - токен сессии

---

Успешный ответ - объект альбома:
```
{
  "album": {
    "album_id": <id_альбома>,
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def albums_read(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    return {
        'album': assert_exists(db, Album, album_id).to_dict()
    }


@router.put('/albums/{album_id}',
            name='Изменение',
            description="""
Изменение альбома.

---

Параметры запроса:
- album_id - ID альбома
- token - токен сессии

Тело запроса:
```
{
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
}
```

---

Успешный ответ - объект альбома после изменений:
```
{
  "album": {
    "album_id": <id_альбома>,
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def albums_update(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    body: AlbumForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    album = assert_exists(db, Album, album_id)

    try:
        album.name = body.name
        album.artist_id = body.artist_id
        album.asset_id = body.asset_id

        db.commit()
        db.refresh(album)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'album_update', {
        'album': str(album.to_dict())
    })

    return {
        'album': album.to_dict()
    }


@router.delete('/albums/{album_id}',
               name='Удаление',
               description="""
Удаление альбома.

---

Параметры запроса:
- album_id - ID альбома
- token - токен сессии

---

Успешный ответ - объект альбома до удаления:
```
{
  "album": {
    "album_id": <id_альбома>,
    "name": "<название>",
    "artist_id": <id_исполнителя>,
    "asset_id": <id_вложения_обложки>
  }
}
```

            """)
async def albums_delete(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    album = assert_exists(db, Album, album_id)

    try:
        db.delete(album)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'album_delete', {
        'album': str(album.to_dict())
    })

    return {
        'album': album.to_dict()
    }


@router.get('/albums/{album_id}/songs',
            name='Список',
            description="""
Список песен на альбоме.

---

Параметры запроса:
- album_id - ID альбома
- token - токен сессии
- page - номер страницы

---

Успешный ответ:
```
{
  "total": <всего_записей>,
  "page": <текущая_страница>,
  "per_page": <записей_на_страницу>,
  "items": [
    <записи>
  ]
}
```


            """)
async def albums_songs(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(Song).where(Song.album_id == album_id))
        songs = db.scalars(
            select(Song).where(Song.album_id == album_id).offset(const.ELEMENTS_PER_PAGE * (page - 1)).limit(
                const.ELEMENTS_PER_PAGE).order_by(
                Song.song_id))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in songs]
    }


"""
SONGS
"""


@router.post('/songs',
             name='Создание',
             description="""
Создание новой песни.

---

Параметры запроса:
- token - токен сессии

Тело запроса:
```
{
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
}
```

---

Успешный ответ - объект песни:
```
{
  "song": {
    "song_id": <id_песни>,
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
  }
}
```

            """)
async def songs_create(
    token: Annotated[str, Query(title='Токен сессии')],
    body: SongForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    try:
        song = Song(name=body.name, album_id=body.album_id, asset_id=body.asset_id)

        db.add(song)
        db.commit()
        db.refresh(song)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'song_create', {
        'song': str(song.to_dict())
    })

    return {
        'song': song.to_dict()
    }


@router.get('/songs/{song_id}',
            name='Информация',
            description="""
Информация о песне.

---

Параметры запроса:
- song_id - ID запроса
- token - токен сессии

---

Успешный ответ - объект песни:
```
{
  "song": {
    "song_id": <id_песни>,
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
  }
}
```

            """)
async def songs_read(
    song_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    return {
        'song': assert_exists(db, Song, song_id).to_dict()
    }


@router.put('/songs/{song_id}',
            name='Изменение',
            description="""
Изменение песни.

---

Параметры запроса:
- song_id - ID песни
- token - токен сессии

Тело запроса:
```
{
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
}
```

---

Успешный ответ - объект песни до изменений:
```
{
  "song": {
    "song_id": <id_песни>,
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
  }
}
```

            """)
async def songs_update(
    song_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    body: SongForm,
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    song = assert_exists(db, Song, song_id)

    try:
        song.name = body.name
        song.album_id = body.album_id
        song.asset_id = body.asset_id

        db.commit()
        db.refresh(song)
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'song_update', {
        'song': str(song.to_dict())
    })

    return {
        'song': song.to_dict()
    }


@router.delete('/songs/{song_id}',
               name='Удаление',
               description="""
Удаление песни.

---

Параметры запроса:
- song_id - ID песни
- token - токен сессии

---

Успешный ответ - объект песни до удаления:
```
{
  "song": {
    "song_id": <id_песни>,
    "name": "<название>",
    "album_id": <id_альбома>,
    "asset_id": <id_вложения_аудио>
  }
}
```

            """)
async def songs_delete(
    song_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_admin(db, token)

    song = assert_exists(db, Song, song_id)

    try:
        db.delete(song)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400)

    log_action(me.user_id, 'song_delete', {
        'song': str(song.to_dict())
    })

    return {
        'song': song.to_dict()
    }


"""
UPLOAD
"""


@router.post('/upload',
             name='Загрузка',
             description="""
Загрузка вложения.

---

Параметры запроса:
- token - токен сессии
- ensure_type - тип файла для проверки

Тело запроса - файл.

---

Успешный ответ - объект вложения:
```
{
  "asset": {
    "asset_id": <id_вложения>,
    "content_type": "<тип_файла>",
    "is_uploaded": <загружен_ли_файл - true/false>
  }
}
```

            """)
async def upload(
    token: Annotated[str, Query(title='Токен сессии')],
    ensure_type: Annotated[str, Query(title='Тип файла для проверки')],
    file: Annotated[UploadFile, File(title='Файл')],
    db: Session = Depends(context.get_db)
):
    assert_is_admin(db, token)

    # Check size and content type
    if file.size > const.MAX_FILE_SIZE or file.content_type != ensure_type:
        raise HTTPException(400)

    # Upload
    s3 = context.ctx.s3

    asset = Asset(content_type=file.content_type)

    try:
        db.add(asset)
        db.commit()
        db.refresh(asset)
    except Exception:
        db.rollback()
        raise HTTPException(500)

    try:
        s3.head_bucket(Bucket=const.BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=const.BUCKET_NAME)
    s3.put_object(Bucket=const.BUCKET_NAME, Key=str(asset.asset_id), Body=await file.read(),
                  ContentType=file.content_type)

    # Confirm
    asset.is_uploaded = True

    try:
        db.commit()
        db.refresh(asset)
    except Exception:
        db.rollback()
        raise HTTPException(500)

    return {
        'asset': asset.to_dict()
    }

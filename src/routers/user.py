from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

import const
import context
from logger import log_user_action as log_action
from models import (
    Asset,
    User,
    Album,
    Artist,
    Song
)
from routers.__base__ import assert_exists

"""
ROUTER
"""

router = APIRouter(prefix='/user', tags=['user'])

"""
HELPERS
"""


def assert_is_user(db: Session, token: str) -> User:
    redis = context.ctx.rs

    user_id = redis.get(token)
    if user_id is None:
        raise HTTPException(401)

    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(401)

    redis.set(token, user.user_id)
    redis.expire(token, const.SESSION_TTL)

    return user


"""
ENDPOINTS
"""


@router.get('/',
            name='Индекс',
            description="""
Возвращает список до 10 самых новых исполнителей, альбомов и песен, добавленных в систему.
Подразумевается для индексной страницы пользователя.

---

Параметры запроса:
- token - токен сессии

---

Успешный ответ:
```
{
  "artists": [
    {
      "artist_id": <id_исполнителя>,
      "name": "<имя>",
      "biography": "<биография>",
      "asset_id": <id_вложения_обложки>
    }
  ],
  "albums": [
    {
      "album_id": <id_альбома>,
      "name": "<имя>",
      "artist_id": <id_исполнителя>,
      "asset_id": <id_вложения_обложки>
    }
  ],
  "songs": [
    {
      "song_id": <id_песни>,
      "name": "<имя>",
      "album_id": <id_альбома>,
      "asset_id": <id_вложения_аудио>
    }
  ]
}
```

            """)
async def index(
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    artists = db.scalars(select(Artist).order_by(desc(Artist.artist_id)).limit(const.INDEX_ARTISTS_COUNT))
    albums = db.scalars(select(Album).order_by(desc(Album.album_id)).limit(const.INDEX_ALBUMS_COUNT))
    songs = db.scalars(select(Song).order_by(desc(Song.song_id)).limit(const.INDEX_SONGS_COUNT))

    return {
        'artists': [x.to_dict() for x in artists],
        'albums': [x.to_dict() for x in albums],
        'songs': [x.to_dict() for x in songs]
    }


@router.get('/me',
            name='Информация',
            description="""
Информация о текущем пользователе.

---

Параметры запроса:
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
async def get_me(
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_user(db, token)
    return {
        'user': me.to_dict()
    }


@router.get('/artist/{artist_id}',
            name='Исполнитель',
            description="""
Информация об исполнителе.

---

Параметры запроса:
- artist_id - ID исполнителя
- token - токен сессии

---

Успешный ответ:
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
async def artist(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    return {
        'artist': assert_exists(db, Artist, artist_id).to_dict(),
    }


@router.get('/artist/{artist_id}/albums',
            name='Альбомы',
            description="""
Возвращает список альбомов исполнителя.

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
async def artist_albums(
    artist_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(Album).where(Album.artist_id == artist_id))
        albums = db.scalars(select(Album).where(Album.artist_id == artist_id).order_by(desc(Album.album_id)).offset(
            const.ELEMENTS_PER_PAGE * (page - 1)).limit(const.ELEMENTS_PER_PAGE))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in albums]
    }


@router.get('/album/{album_id}',
            name='Альбом',
            description="""
Информация об альбоме.

---

Параметры запроса:
- album_id - ID альбома
- token - токен сессии

---

Успешный ответ:
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
async def album(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    return {
        'album': assert_exists(db, Album, album_id).to_dict(),
    }


@router.get('/album/{album_id}/songs',
            name='Песни',
            description="""
Песни на альбоме.

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
async def album_songs(
    album_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    page: Annotated[int, Query(title='Номер страницы', min=1)] = 1,
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    try:
        total = db.scalar(select(func.count()).select_from(Song).where(Song.album_id == album_id))
        songs = db.scalars(select(Song).where(Song.album_id == album_id).order_by(Song.song_id).offset(
            const.ELEMENTS_PER_PAGE * (page - 1)).limit(const.ELEMENTS_PER_PAGE))
    except Exception:
        raise HTTPException(400)

    return {
        'total': total,
        'page': page,
        'per_page': const.ELEMENTS_PER_PAGE,
        'items': [x.to_dict() for x in songs]
    }


@router.get('/song/{song_id}',
            name='Песня',
            description="""
Информация о песне.

---

Параметры запроса:
- song_id - ID песни
- token - токен сессии

---

Успешный ответ:
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
async def song(
    song_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    return {
        'song': assert_exists(db, Song, song_id).to_dict(),
    }


@router.get('/asset/{asset_id}',
            name='Вложение',
            description="""
Получить вложение.

---

Параметры запроса.
- asset_id - ID вложения
- token - токен сессии

---

В случае успешного ответа будет поток.

            """)
async def asset(
    asset_id: int,
    token: Annotated[str, Query(title='Токен сессии')],
    _range: str | None = Header(None, alias='range'),
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    _asset = db.get(Asset, asset_id)
    if _asset is None or not _asset.is_uploaded:
        raise HTTPException(404)

    s3 = context.ctx.s3

    file_size = s3.head_object(
        Bucket=const.BUCKET_NAME,
        Key=str(_asset.asset_id)
    )['ContentLength']

    resp_code = 200
    resp_headers = {
        'accept-ranges': 'bytes',
        'content-encoding': 'identity',
        'content-length': str(file_size),
        'access-control-expose-headers': (
            'content-type, accept-ranges, content-length, '
            'content-range, content-encoding'
        )
    }

    start = 0
    end = file_size - 1

    if _range is not None:
        try:
            p = _range.replace('bytes=', '').split('-')
            start = int(p[0]) if p[0] else 0
            end = int(p[1]) if p[1] else file_size - 1
            if start > end or start < 0 or end > file_size - 1:
                raise Exception
        except Exception:
            raise HTTPException(416)

        resp_code = 206
        resp_headers['content-length'] = str(end - start + 1)
        resp_headers['content-range'] = f'bytes {start}-{end}/{file_size}'

    obj = s3.get_object(
        Bucket=const.BUCKET_NAME,
        Key=str(_asset.asset_id),
        Range=f'bytes={start}-{end}'
    )

    return StreamingResponse(
        content=obj['Body'],
        status_code=resp_code,
        headers=resp_headers,
        media_type=obj['ContentType']
    )


@router.get('/search',
            name='Поиск',
            description="""
Поиск исполнителей, альбомов и песен в системе.

---

Параметры запроса:
- token - токен сессии
- q - запрос (часть требуемого названия)

---

Успешный ответ:
```
{
  "results": [
    {
        "id": id_записи,
        "type": "тип_записи",
        "data": {
            <данные_для_отображения_пользователю>
        }
    },
    {
      "id": 1,
      "type": "artist",
      "data": {
        "name": "<имя_исполнителя>"
      }
    },
    {
      "id": 1,
      "type": "album",
      "data": {
        "name": "<имя_альбома>",
        "artist": "<имя_исполнителя>"
      }
    },
    {
      "id": 1,
      "type": "song",
      "data": {
        "name": "<название_песни>",
        "artist": "<имя_исполнителя>"
      }
    }
  ]
}
```

            """)
async def search(
    token: Annotated[str, Query(title='Токен сессии')],
    q: Annotated[str, Query(title='Запрос')],
    db: Session = Depends(context.get_db)
):
    assert_is_user(db, token)

    es = context.ctx.es
    results = []

    if es.indices.exists(index=const.ELASTICSEARCH_INDEX):
        response = context.ctx.es.search(
            index=const.ELASTICSEARCH_INDEX,
            body={
                'size': const.ELASTICSEARCH_SEARCH_LIMIT,
                'query': {
                    'wildcard': {
                        'keyword': '*' + q + '*',
                    }
                }
            }
        )
        for hit in response['hits']['hits']:
            cls, uid = hit['_id'].split('_')
            result = {
                'id': int(uid),
                'type': cls,
                'data': hit['_source']['data'],
            }
            results.append(result)

    return {
        'results': results
    }


@router.delete('/logout',
               name='Выход',
               description="""
Выход из системы.

---

Параметры запроса:
- token - токен сессии

               """)
async def logout(
    token: Annotated[str, Query(title='Токен сессии')],
    db: Session = Depends(context.get_db)
):
    me = assert_is_user(db, token)

    context.ctx.rs.delete(token)

    log_action(me.user_id, 'logout')

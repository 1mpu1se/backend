import pytest
from unittest.mock import MagicMock, patch

from src.models.album import Album
from src.models.asset import Asset
from src.models.artist import Artist
from src import const

# ------------------ Фикстуры ------------------

@pytest.fixture
def fake_db():
    class FakeDB:
        def __init__(self):
            self.assets = {}
            self.artists = {}
        def get(self, cls, id_):
            if cls == Asset:
                return self.assets.get(id_)
            if cls == Artist:
                return self.artists.get(id_)
            return None
    return FakeDB()

@pytest.fixture
def fake_asset():
    a = Asset()
    a.asset_id = 1
    a.is_uploaded = True
    a.content_type = const.FILE_TYPE_IMAGE
    return a

@pytest.fixture
def fake_artist():
    a = Artist()
    a.artist_id = 1
    a.name = "Test Artist"
    return a

@pytest.fixture
def fake_album():
    a = Album()
    a.album_id = 1
    a.name = "Test Album"
    a.artist_id = 1
    a.asset_id = 1
    return a

# ------------------ Тесты ------------------

def test_to_dict(fake_album):
    d = fake_album.to_dict()
    assert d['album_id'] == 1
    assert d['name'] == "Test Album"
    assert d['artist_id'] == 1
    assert d['asset_id'] == 1

def test_name_set_validation():
    album = Album()
    # Короткое имя
    with pytest.raises(ValueError):
        album.name = "A"
    # Длинное имя
    with pytest.raises(ValueError):
        album.name = "A"*1000
    # Корректное имя
    album.name = "Valid Name"
    assert album.name == "Valid Name"

def test_after_insert_calls_es(fake_db, fake_artist, fake_album):
    fake_db.artists[fake_artist.artist_id] = fake_artist
    fake_album.artist_id = fake_artist.artist_id

    fake_es = MagicMock()

    with patch('src.context.ctx') as mock_ctx:
        mock_ctx.es = fake_es

        from src.models.album import after_change
        from sqlalchemy.orm import attributes

        # Патчим state.session на fake_db
        state = MagicMock()
        state.session = fake_db
        with patch('sqlalchemy.orm.attributes.instance_state', return_value=state):
            after_change(None, None, fake_album)

        fake_es.index.assert_called_once_with(
            index=const.ELASTICSEARCH_INDEX,
            id='album_' + str(fake_album.album_id),
            document={'keyword': fake_album.name, 'data': {'name': fake_album.name, 'artist': fake_artist.name}}
        )

def test_before_delete_calls_es(fake_album):
    fake_es = MagicMock()
    with patch('src.context.ctx') as mock_ctx:
        mock_ctx.es = fake_es

        from src.models.album import before_delete
        before_delete(None, None, fake_album)

        fake_es.delete.assert_called_once_with(
            index=const.ELASTICSEARCH_INDEX,
            id='album_' + str(fake_album.album_id)
        )

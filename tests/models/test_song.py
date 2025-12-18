import pytest
from unittest.mock import MagicMock, patch
from src.models.song import Song, name_set, before_change, after_change, before_delete
from src.models.asset import Asset
from src.models.album import Album
from src.models.artist import Artist
from src import const, context

# ------------------ Фикстуры ------------------

@pytest.fixture
def fake_asset():
    a = Asset()
    a.asset_id = 1
    a.is_uploaded = True
    a.content_type = const.FILE_TYPE_AUDIO
    return a

@pytest.fixture
def fake_artist():
    a = Artist()
    a.artist_id = 1
    a.name = "Test Artist"
    return a

@pytest.fixture
def fake_album(fake_artist):
    a = Album()
    a.album_id = 1
    a.name = "Test Album"
    a.artist_id = fake_artist.artist_id
    a.asset_id = 1
    return a

@pytest.fixture
def fake_song():
    s = Song()
    s.song_id = 1
    s.name = "Test Song"
    s.album_id = 1
    s.asset_id = 1
    return s

@pytest.fixture
def fake_db(fake_asset, fake_album, fake_artist):
    class FakeDB:
        def __init__(self):
            self.assets = {1: fake_asset}
            self.albums = {1: fake_album}
            self.artists = {1: fake_artist}
        def get(self, cls, id_):
            if cls == Asset:
                return self.assets.get(id_)
            if cls == Album:
                return self.albums.get(id_)
            if cls == Artist:
                return self.artists.get(id_)
            return None
    return FakeDB()

# ------------------ Тесты ------------------

def test_to_dict(fake_song):
    d = fake_song.to_dict()
    assert d['song_id'] == 1
    assert d['name'] == "Test Song"
    assert d['album_id'] == 1
    assert d['asset_id'] == 1

def test_name_set_validation():
    song = Song()
    with pytest.raises(ValueError):
        song.name = "A"
    with pytest.raises(ValueError):
        song.name = "A"*1000
    song.name = "Valid Name"
    assert song.name == "Valid Name"

def test_before_insert_update(fake_song, fake_db, fake_album, fake_artist):
    state = MagicMock()
    state.session = fake_db
    with patch('sqlalchemy.orm.attributes.instance_state', return_value=state):
        before_change(None, None, fake_song)

def test_after_insert_update_calls_es(fake_song, fake_db, fake_album, fake_artist):
    state = MagicMock()
    state.session = fake_db

    fake_es = MagicMock()
    fake_ctx = MagicMock()
    fake_ctx.es = fake_es

    with patch('src.context.ctx', fake_ctx):
        from src.models.song import after_change
        from sqlalchemy.orm import attributes
        with patch('sqlalchemy.orm.attributes.instance_state', return_value=state):
            after_change(None, None, fake_song)

    fake_es.index.assert_called_once_with(
        index=const.ELASTICSEARCH_INDEX,
        id='song_' + str(fake_song.song_id),
        document={'keyword': fake_song.name, 'data': {'name': fake_song.name, 'artist': fake_artist.name}}
    )

def test_before_delete_calls_es(fake_song):
    fake_es = MagicMock()
    fake_ctx = MagicMock()
    fake_ctx.es = fake_es

    with patch('src.context.ctx', fake_ctx):
        from src.models.song import before_delete
        before_delete(None, None, fake_song)

    fake_es.delete.assert_called_once_with(
        index=const.ELASTICSEARCH_INDEX,
        id='song_' + str(fake_song.song_id)
    )
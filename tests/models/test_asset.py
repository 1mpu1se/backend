import pytest
from unittest.mock import MagicMock, patch

from src.models.artist import Artist
from src.models.asset import Asset
from src import const

# ------------------ Фикстуры ------------------

@pytest.fixture
def fake_db():
    class FakeDB:
        def __init__(self):
            self.assets = {}
        def get(self, cls, id_):
            if cls == Asset:
                return self.assets.get(id_)
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
    a.biography = "Some biography"
    a.asset_id = 1
    return a

# ------------------ Тесты ------------------

def test_to_dict(fake_artist):
    d = fake_artist.to_dict()
    assert d['artist_id'] == 1
    assert d['name'] == "Test Artist"
    assert d['biography'] == "Some biography"
    assert d['asset_id'] == 1

def test_name_validation():
    artist = Artist()
    # Слишком короткое
    with pytest.raises(ValueError):
        artist.name = "A"
    # Слишком длинное
    with pytest.raises(ValueError):
        artist.name = "A"*1000
    # Валидное
    artist.name = "Valid Name"
    assert artist.name == "Valid Name"

def test_biography_validation():
    artist = Artist()
    # Слишком короткая
    with pytest.raises(ValueError):
        artist.biography = "A"
    # Слишком длинная
    with pytest.raises(ValueError):
        artist.biography = "A"*10000
    # Валидная
    artist.biography = "Valid biography"
    assert artist.biography == "Valid biography"

def test_before_insert_and_update(fake_db, fake_artist, fake_asset):
    fake_db.assets[fake_asset.asset_id] = fake_asset
    from src.models.artist import before_change
    from sqlalchemy.orm import attributes

    state = MagicMock()
    state.session = fake_db
    with patch('sqlalchemy.orm.attributes.instance_state', return_value=state):
        before_change(None, None, fake_artist)  # Не должно падать

def test_after_insert_calls_es(fake_artist):
    fake_es = MagicMock()
    with patch('src.context.ctx') as mock_ctx:
        mock_ctx.es = fake_es

        from src.models.artist import after_change
        after_change(None, None, fake_artist)

        fake_es.index.assert_called_once_with(
            index=const.ELASTICSEARCH_INDEX,
            id='artist_' + str(fake_artist.artist_id),
            document={'keyword': fake_artist.name, 'data': {'name': fake_artist.name}}
        )

def test_before_delete_calls_es(fake_artist):
    fake_es = MagicMock()
    with patch('src.context.ctx') as mock_ctx:
        mock_ctx.es = fake_es

        from src.models.artist import before_delete
        before_delete(None, None, fake_artist)

        fake_es.delete.assert_called_once_with(
            index=const.ELASTICSEARCH_INDEX,
            id='artist_' + str(fake_artist.artist_id)
        )

import pytest
from pydantic import ValidationError
from src.forms.album import AlbumForm
from src import const

def test_album_form_valid():
    form = AlbumForm(
        name="Valid Album Name",
        artist_id=1,
        asset_id=1
    )
    assert form.name == "Valid Album Name"
    assert form.artist_id == 1
    assert form.asset_id == 1

def test_album_form_name_too_short():
    with pytest.raises(ValidationError):
        AlbumForm(
            name="A",  # слишком короткое имя
            artist_id=1,
            asset_id=1
        )

def test_album_form_name_too_long():
    with pytest.raises(ValidationError):
        AlbumForm(
            name="A" * (const.ALBUM_NAME_LENGTH[1] + 1),  # слишком длинное имя
            artist_id=1,
            asset_id=1
        )

def test_album_form_negative_ids():
    with pytest.raises(ValidationError):
        AlbumForm(
            name="Valid Name",
            artist_id=-1,
            asset_id=-1
        )

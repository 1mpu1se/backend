import pytest
from pydantic import ValidationError
from src.forms.song import SongForm
from src import const

def test_song_form_valid():
    form = SongForm(
        name="Valid Song",
        album_id=1,
        asset_id=1
    )
    assert form.name == "Valid Song"
    assert form.album_id == 1
    assert form.asset_id == 1

def test_song_form_name_too_short():
    with pytest.raises(ValidationError):
        SongForm(
            name="a",  # слишком короткое название
            album_id=1,
            asset_id=1
        )

def test_song_form_name_too_long():
    with pytest.raises(ValidationError):
        SongForm(
            name="a" * (const.SONG_NAME_LENGTH[1] + 1),  # слишком длинное название
            album_id=1,
            asset_id=1
        )

def test_song_form_negative_album_id():
    with pytest.raises(ValidationError):
        SongForm(
            name="Valid Song",
            album_id=-1,  # недопустимый отрицательный ID
            asset_id=1
        )

def test_song_form_negative_asset_id():
    with pytest.raises(ValidationError):
        SongForm(
            name="Valid Song",
            album_id=1,
            asset_id=-1  # недопустимый отрицательный ID
        )

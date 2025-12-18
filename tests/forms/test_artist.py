import pytest
from pydantic import ValidationError
from src.forms.artist import ArtistForm
from src import const

def test_artist_form_valid():
    form = ArtistForm(
        name="Valid Artist",
        biography="This is a valid biography.",
        asset_id=1
    )
    assert form.name == "Valid Artist"
    assert form.biography == "This is a valid biography."
    assert form.asset_id == 1

def test_artist_form_name_too_short():
    with pytest.raises(ValidationError):
        ArtistForm(
            name="A",  # слишком короткое имя
            biography="Valid biography",
            asset_id=1
        )

def test_artist_form_name_too_long():
    with pytest.raises(ValidationError):
        ArtistForm(
            name="A" * (const.ARTIST_NAME_LENGTH[1] + 1),  # слишком длинное имя
            biography="Valid biography",
            asset_id=1
        )

def test_artist_form_biography_too_short():
    with pytest.raises(ValidationError):
        ArtistForm(
            name="Valid Name",
            biography="A",  # слишком короткая биография
            asset_id=1
        )

def test_artist_form_biography_too_long():
    with pytest.raises(ValidationError):
        ArtistForm(
            name="Valid Name",
            biography="A" * (const.ARTIST_BIOGRAPHY_LENGTH[1] + 1),  # слишком длинная биография
            asset_id=1
        )

def test_artist_form_negative_asset_id():
    with pytest.raises(ValidationError):
        ArtistForm(
            name="Valid Name",
            biography="Valid biography",
            asset_id=-1  # отрицательный asset_id
        )

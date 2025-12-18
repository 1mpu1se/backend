import pytest
from pydantic import ValidationError
from src.forms.upload import UploadForm

def test_upload_form_empty_type():
    with pytest.raises(ValidationError):
        UploadForm(
            ensure_type=""  # пустое значение
        )

def test_upload_form_non_empty_type():
    form = UploadForm(
        ensure_type="1"  # 1 символ
    )
    assert form.ensure_type == "1"

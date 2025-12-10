from pydantic import BaseModel, Field


class UploadForm(BaseModel):
    ensure_type: str = Field(title='Тип загружаемого файла для проверки', min_length=1)

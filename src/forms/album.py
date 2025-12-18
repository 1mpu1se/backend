from pydantic import BaseModel, Field

import src.const as const


class AlbumForm(BaseModel):
    name: str = Field(title='Название альбома', min_length=const.ALBUM_NAME_LENGTH[0],
                      max_length=const.ALBUM_NAME_LENGTH[1])
    artist_id: int = Field(title='ID исполнителя', ge=0)
    asset_id: int = Field(title='ID файла обложки', ge=0)

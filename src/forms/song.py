from pydantic import BaseModel, Field

import src.const as const


class SongForm(BaseModel):
    name: str = Field(title='Название композиции', min_length=const.SONG_NAME_LENGTH[0],
                      max_length=const.SONG_NAME_LENGTH[1])
    album_id: int = Field(title='ID альбома', ge=0)
    asset_id: int = Field(title='ID файла аудио', ge=0)

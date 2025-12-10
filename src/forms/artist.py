from pydantic import BaseModel, Field

import const


class ArtistForm(BaseModel):
    name: str = Field(title='Имя исполнителя', min_length=const.ARTIST_NAME_LENGTH[0],
                      max_length=const.ARTIST_NAME_LENGTH[1])
    biography: str = Field(title='Биография', min_length=const.ARTIST_BIOGRAPHY_LENGTH[0],
                           max_length=const.ARTIST_BIOGRAPHY_LENGTH[1])
    asset_id: int = Field(title='ID файла обложки', ge=0)

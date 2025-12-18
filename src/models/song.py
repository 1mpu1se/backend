from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship, attributes

import src.const as const
import src.context as context
from src.models.__base__ import Base
from src.models.album import Album
from src.models.artist import Artist
from src.models.asset import Asset


class Song(Base):
    __tablename__ = 'songs'

    song_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    album_id: Mapped[int]
    asset_id: Mapped[int]

    album = relationship(
        'Album',
        primaryjoin='foreign(Song.album_id)==Album.album_id',
        back_populates='songs'
    )

    asset = relationship(
        'Asset',
        primaryjoin='foreign(Song.asset_id)==Asset.asset_id'
    )

    def to_dict(self) -> dict:
        return {
            'song_id': self.song_id,
            'name': self.name,
            'album_id': self.album_id,
            'asset_id': self.asset_id
        }


@event.listens_for(Song.name, 'set')
def name_set(target, value, oldvalue, initiator):
    length = len(value)
    if length < const.SONG_NAME_LENGTH[0] or length > const.SONG_NAME_LENGTH[1]:
        raise ValueError(f'Song name must be between {const.SONG_NAME_LENGTH} characters long')


@event.listens_for(Song, 'before_insert')
@event.listens_for(Song, 'before_update')
def before_change(mapper, connection, target):
    db = attributes.instance_state(target).session

    asset = db.get(Asset, target.asset_id)
    if asset is None or not asset.is_uploaded or asset.content_type != const.FILE_TYPE_AUDIO:
        raise ValueError('Invalid asset has been provided for the song')

    album = db.get(Album, target.album_id)
    if album is None:
        raise ValueError('Invalid album has been provided for the song')


@event.listens_for(Song, 'after_insert')
@event.listens_for(Song, 'after_update')
def after_change(mapper, connection, target):
    db = attributes.instance_state(target).session
    album = db.get(Album, target.album_id)
    artist = db.get(Artist, album.artist_id)
    context.ctx.es.index(
        index=const.ELASTICSEARCH_INDEX,
        id='song_' + str(target.song_id),
        document={
            'keyword': target.name,
            'data': {
                'name': target.name,
                'artist': artist.name
            }
        }
    )


@event.listens_for(Song, 'before_delete')
def before_delete(mapper, connection, target):
    context.ctx.es.delete(
        index=const.ELASTICSEARCH_INDEX,
        id='song_' + str(target.song_id)
    )

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship, attributes

import src.const as const
import src.context as context
from src.models.__base__ import Base
from src.models.artist import Artist
from src.models.asset import Asset


class Album(Base):
    __tablename__ = 'albums'

    album_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    artist_id: Mapped[int]
    asset_id: Mapped[int]

    cover = relationship(
        'Asset',
        primaryjoin='foreign(Album.asset_id)==Asset.asset_id'
    )

    artist = relationship(
        'Artist',
        primaryjoin='foreign(Album.artist_id)==Artist.artist_id',
        back_populates='albums'
    )

    songs = relationship(
        'Song',
        primaryjoin='Album.album_id==foreign(Song.album_id)',
        back_populates='album',
        cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict:
        return {
            'album_id': self.album_id,
            'name': self.name,
            'artist_id': self.artist_id,
            'asset_id': self.asset_id,
        }


@event.listens_for(Album.name, 'set')
def name_set(target, value, oldvalue, initiator):
    length = len(value)
    if length < const.ALBUM_NAME_LENGTH[0] or length > const.ALBUM_NAME_LENGTH[1]:
        raise ValueError(f'Album name must be between {const.ALBUM_NAME_LENGTH} characters long')


@event.listens_for(Album, 'before_insert')
@event.listens_for(Album, 'before_update')
def before_change(mapper, connection, target):
    db = attributes.instance_state(target).session

    asset = db.get(Asset, target.asset_id)
    if asset is None or not asset.is_uploaded or asset.content_type != const.FILE_TYPE_IMAGE:
        raise ValueError('Invalid asset has been provided for the album')

    artist = db.get(Artist, target.artist_id)
    if artist is None:
        raise ValueError('Invalid artist has been provided for the album')


@event.listens_for(Album, 'after_insert')
@event.listens_for(Album, 'after_update')
def after_change(mapper, connection, target):
    db = attributes.instance_state(target).session
    artist = db.get(Artist, target.artist_id)
    context.ctx.es.index(
        index=const.ELASTICSEARCH_INDEX,
        id='album_' + str(target.album_id),
        document={
            'keyword': target.name,
            'data': {
                'name': target.name,
                'artist': artist.name
            }
        }
    )


@event.listens_for(Album, 'before_delete')
def before_delete(mapper, connection, target):
    context.ctx.es.delete(
        index=const.ELASTICSEARCH_INDEX,
        id='album_' + str(target.album_id)
    )

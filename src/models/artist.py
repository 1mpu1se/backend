from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship, attributes

import src.const as const
import src.context as context
from src.models.__base__ import Base
from src.models.asset import Asset


class Artist(Base):
    __tablename__ = 'artists'

    artist_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    biography: Mapped[str]
    asset_id: Mapped[int]

    cover = relationship(
        'Asset',
        primaryjoin='foreign(Artist.asset_id)==Asset.asset_id'
    )

    albums = relationship(
        'Album',
        primaryjoin='Artist.artist_id==foreign(Album.artist_id)',
        back_populates='artist',
        cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict:
        return {
            'artist_id': self.artist_id,
            'name': self.name,
            'biography': self.biography,
            'asset_id': self.asset_id
        }


@event.listens_for(Artist.name, 'set')
def name_set(target, value, oldvalue, initiator):
    length = len(value)
    if length < const.ARTIST_NAME_LENGTH[0] or length > const.ARTIST_NAME_LENGTH[1]:
        raise ValueError(f'Artist name must be between {const.ARTIST_NAME_LENGTH} characters long')


@event.listens_for(Artist.biography, 'set')
def biograpy_set(target, value, oldvalue, initiator):
    length = len(value)
    if length < const.ARTIST_BIOGRAPHY_LENGTH[0] or length > const.ARTIST_BIOGRAPHY_LENGTH[1]:
        raise ValueError(f'Artist biography must be between {const.ARTIST_BIOGRAPHY_LENGTH} characters long')


@event.listens_for(Artist, 'before_insert')
@event.listens_for(Artist, 'before_update')
def before_change(mapper, connection, target):
    db = attributes.instance_state(target).session
    asset = db.get(Asset, target.asset_id)
    if asset is None or not asset.is_uploaded or asset.content_type != const.FILE_TYPE_IMAGE:
        raise ValueError('Invalid asset has been provided for the artist')


@event.listens_for(Artist, 'after_insert')
@event.listens_for(Artist, 'after_update')
def after_change(mapper, connection, target):
    context.ctx.es.index(
        index=const.ELASTICSEARCH_INDEX,
        id='artist_' + str(target.artist_id),
        document={
            'keyword': target.name,
            'data': {
                'name': target.name
            }
        }
    )


@event.listens_for(Artist, 'before_delete')
def before_delete(mapper, connection, target):
    context.ctx.es.delete(
        index=const.ELASTICSEARCH_INDEX,
        id='artist_' + str(target.artist_id)
    )

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column

from models.__base__ import Base


class Asset(Base):
    __tablename__ = 'assets'

    asset_id: Mapped[int] = mapped_column(primary_key=True)
    content_type: Mapped[str]
    is_uploaded: Mapped[bool] = mapped_column(default=False)

    def to_dict(self) -> dict:
        return {
            'asset_id': self.asset_id,
            'content_type': self.content_type,
            'is_uploaded': self.is_uploaded
        }


@event.listens_for(Asset, 'before_delete')
def before_delete(mapper, connection, target):
    raise RuntimeError('Assets cannot be deleted')

import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.postgres import db


class IdMixin(db.Model):
    __abstract__ = True

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class CreatedTimeMixin(db.Model):
    __abstract__ = True

    created = db.Column(db.DateTime, default=db.func.now())


class UpdatedTimeMixin(db.Model):
    __abstract__ = True

    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

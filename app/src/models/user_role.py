import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.postgres import db

user_role = db.Table(
    "user_role",
    db.Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ),
    db.Column("user_id", db.ForeignKey("user.id")),
    db.Column("role_id", db.ForeignKey("role.id")),
    db.Column("created", db.DateTime, default=db.func.now()),
)

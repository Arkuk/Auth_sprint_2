import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint

from db.postgres import db
from models.mixins import CreatedTimeMixin, IdMixin


'''def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_windows" PARTITION OF "user_login_history" FOR VALUES IN ('windows')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_android" PARTITION OF "user_login_history" FOR VALUES IN ('android')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_macos" PARTITION OF "user_login_history" FOR VALUES IN ('macos')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_macos" PARTITION OF "user_login_history" FOR VALUES IN ('linux')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_unknown" PARTITION OF "user_login_history" FOR VALUES IN ('unknown')"""
    )'''


class UserLoginHistory(CreatedTimeMixin):
    __tablename__ = "user_login_history"

    __table_args__ = (
        UniqueConstraint('id', 'user_platform'),
        {
            'postgresql_partition_by': 'LIST (user_platform)',
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user_agent = db.Column(db.String(length=256))
    user_platform = db.Column(db.Text, primary_key=True)

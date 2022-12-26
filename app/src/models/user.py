import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.postgres import db
from models.mixins import CreatedTimeMixin, IdMixin, UpdatedTimeMixin
from models.role import Role
from models.user_role import user_role


class User(IdMixin, CreatedTimeMixin, UpdatedTimeMixin):
    __tablename__ = "user"

    username = db.Column(db.String(length=56), unique=True, nullable=False)
    password = db.Column(db.String(length=256), nullable=False)
    roles = db.relationship(Role, secondary=user_role, backref="users")
    social_account = db.relationship('SocialAccount', backref='user', lazy=True)


def create_partition(target, connection, **kw) -> None:
    """ creating partition by social_account """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_yandex" PARTITION OF "social_account" FOR VALUES IN ('yandex')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_google" PARTITION OF "social_account" FOR VALUES IN ('vk')"""
    )


class SocialAccount(CreatedTimeMixin):
    __tablename__ = 'social_account'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'),
                      {
                          'postgresql_partition_by': 'LIST (social_name)',
                          'listeners': [('after_create', create_partition)],
                      })
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, default=db.func.now())
    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, primary_key=True)

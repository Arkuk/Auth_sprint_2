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


class SocialAccount(IdMixin, CreatedTimeMixin):
    __tablename__ = 'social_account'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'), )

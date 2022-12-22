from db.postgres import db
from models.mixins import CreatedTimeMixin, IdMixin, UpdatedTimeMixin
from models.role import Role
from models.user_role import user_role


class User(IdMixin, CreatedTimeMixin, UpdatedTimeMixin):
    __tablename__ = "user"

    username = db.Column(db.String(length=56), unique=True, nullable=False)
    password = db.Column(db.String(length=256), nullable=False)
    roles = db.relationship(Role, secondary=user_role, backref="users")

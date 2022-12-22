from sqlalchemy.dialects.postgresql import UUID

from db.postgres import db
from models.mixins import CreatedTimeMixin, IdMixin


class UserLoginHistory(IdMixin, CreatedTimeMixin):
    __tablename__ = "user_login_history"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user_agent = db.Column(db.String(length=256))

from dataclasses import dataclass

from flask_restx import abort
from flask_restx._http import HTTPStatus
from sqlalchemy.exc import NoResultFound

from db.postgres import db
from models.user import User
from models.user_login_history import UserLoginHistory


@dataclass
class PaginationArgs:
    page: str
    per_page: str


class UserService:

    @staticmethod
    def get_detail_user(user_id: str):
        try:
            user = db.session.execute(db.select(User).filter_by(id=user_id)).one()
            return user[0]
        except NoResultFound:
            abort(HTTPStatus.NOT_FOUND, "Not found")

    @staticmethod
    def get_login_history(user_id: str, body: dict):
        try:
            pagination_args = PaginationArgs(**body)
            queryset = UserLoginHistory.query.filter_by(user_id=user_id)
            paginator = queryset.paginate(
                page=pagination_args.page, per_page=pagination_args.per_page, error_out=False
            )
            return paginator.items
        except NoResultFound:
            abort(HTTPStatus.NOT_FOUND, "Not found")


user_service = UserService()

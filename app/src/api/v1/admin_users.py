from flask_restx import Namespace, Resource
from flask_restx._http import HTTPStatus

from schemas.user import user_schema_response
from services.admin import admin_service
from services.auth import auth_service

api = Namespace("API для управления доступами. Юзеры")

users = api.model("Users", user_schema_response)


@api.route("/users")
class User(Resource):
    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.marshal_with(users, code=HTTPStatus.OK)
    @api.response(int(HTTPStatus.NOT_FOUND), "Not Found")
    def get(self):
        result = admin_service.get_list_data()
        return result, 200

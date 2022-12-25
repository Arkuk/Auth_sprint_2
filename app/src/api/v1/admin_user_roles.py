from flask_restx import Namespace, Resource
from flask_restx._http import HTTPStatus

from schemas.user_roles import user_roles_schema
from services.auth import auth_service
from services.user_roles import user_roles

api = Namespace("API для управления доступами. Управляение ролями пользователей")

user_roles_schema = api.model("UserRoleResponse", user_roles_schema)


@api.route("/users/<user_id>/roles")
class Roles(Resource):
    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.marshal_with(user_roles_schema, code=int(HTTPStatus.OK))
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def get(self, user_id):
        roles = user_roles.get_user_roles(user_id)
        return roles, 200

    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.expect(user_roles_schema)
    @api.response(int(HTTPStatus.CREATED), "Role assigned to user")
    @api.response(int(HTTPStatus.CONFLICT), "User already has this role")
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def post(self, user_id):
        roles = user_roles.assign_role(user_id, api.payload)
        return roles, 201

    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.expect(user_roles_schema)
    @api.response(int(HTTPStatus.OK), "Role discarded from user")
    @api.response(int(HTTPStatus.CONFLICT), "No role to discard from user")
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def delete(self, user_id):
        roles = user_roles.discard_role(user_id, api.payload)
        return roles, 204

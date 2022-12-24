from flask_restx import Namespace, Resource
from flask_restx._http import HTTPStatus

from schemas.role import (role_schema_create, role_schema_expect,
                          role_schema_response)
from services.auth import auth_service
from services.roles import role_service

api = Namespace("API для сайта и личного кабинета. Управление ролями", validate=True)

role_schema_expect = api.model("RoleExpect", role_schema_expect)
role_schema_create = api.model("RoleCreated", role_schema_create)
role_schema_response = api.model("RoleRespose", role_schema_response)


@api.route("/roles")
class RoleCRUD(Resource):
    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.expect(role_schema_create)
    @api.marshal_with(role_schema_response, code=int(HTTPStatus.CREATED))
    @api.response(
        int(HTTPStatus.CONFLICT),
        "Role is already exist! Please choose another role name",
    )
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def post(self):
        result = role_service.create_role(api.payload)
        return result, 201

    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.marshal_with(role_schema_response, code=int(HTTPStatus.OK))
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def get(self):
        result = role_service.get_roles_list()
        return result, 200

    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.expect(role_schema_response)
    @api.marshal_with(role_schema_response, code=int(HTTPStatus.OK))
    @api.response(int(HTTPStatus.CONFLICT), "No role to update")
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    def put(self):
        result = role_service.update_role(api.payload)
        return result, 200

    @auth_service.verify_token()
    @auth_service.check_roles(["admin"])
    @api.expect(role_schema_expect)
    @api.marshal_with(role_schema_expect, code=int(HTTPStatus.OK))
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    @api.response(
        int(HTTPStatus.CONFLICT), "Cannot delete the role, role assigned to user"
    )
    def delete(self):
        result = role_service.delete_role(api.payload)
        return result, 204

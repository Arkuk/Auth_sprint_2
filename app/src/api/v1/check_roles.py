from flask_restx import Namespace, Resource, reqparse
from flask_restx._http import HTTPStatus

from services.auth import auth_service
from schemas.token import token_valid

api = Namespace("Ручка для интеграции сервисов")

token_valid = api.model("TokenValid", token_valid)

parser = reqparse.RequestParser()
parser.add_argument("role", location="args")


@api.route("/check_roles/<role>")
class CheckRoles(Resource):
    @auth_service.verify_token()
    @api.marshal_with(token_valid, code=HTTPStatus.OK)
    @api.response(int(HTTPStatus.NO_CONTENT), "Request fulfilled, nothing follows")
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    @api.response(int(HTTPStatus.UNAUTHORIZED), "Token is not corrected\n"
                                                "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY), "Token is not corrected\n"
                                                        "The token has expired")
    @api.doc('Другой сервис на эту ручку отправляет в хедаре ассепт токен, и параметролм роль'
             'данная ручка проверяет токен и роль в случае успеха возращает 200,'
             'иначе 401 или 422, 204')
    def post(self, role):
        if auth_service.func_check_roles([role]):
            return 200
        else:
            return int(HTTPStatus.NO_CONTENT)

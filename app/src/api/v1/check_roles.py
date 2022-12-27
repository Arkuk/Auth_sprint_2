from flask_restx import Namespace, Resource, reqparse
from flask_restx._http import HTTPStatus
from services.auth import auth_service

api = Namespace("Ручка для интеграции сервисов")
api.doc('Другой сервис на эту ручку отправляет в хедаре ассепт токен, и параметролм роль'
        'данная ручка проверяет токен и роль в случае успеха возращает 200,'
        'иначе 401 или 422, 204')
parser = reqparse.RequestParser()

parser.add_argument("role", location="args")


@api.route("/check_roles/<role>")
class CheckRoles(Resource):
    @auth_service.verify_token()
    @api.response(int(HTTPStatus.NO_CONTENT),
                  "Request fulfilled, nothing follows")
    @api.response(int(HTTPStatus.OK), "Token is valid")
    @api.response(int(HTTPStatus.FORBIDDEN), "Permission denied")
    @api.response(int(HTTPStatus.UNAUTHORIZED), "Token is not corrected\n"
                                                "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY), "Token is not corrected\n"
                                                        "The token has expired")
    def post(self, role):
        if auth_service.func_check_roles([role]):
            return int(HTTPStatus.OK)
        else:
            return int(HTTPStatus.NO_CONTENT)

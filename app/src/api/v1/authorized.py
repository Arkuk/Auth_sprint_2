from flask_jwt_extended import get_jwt
from flask_restx import Namespace, Resource, reqparse
from flask_restx._http import HTTPStatus

from schemas.token import responses_tokens
from schemas.user import (change_password_schema, login_history_schema,
                          user_schema_long_response)
from services.auth import auth_service
from services.user import user_service
from core.config import settings

api = Namespace(
    "API для сайта и личного кабинета. Авторизованные пользователи")

user_schema_long_response = api.model(
    "UserSchemaLongResponse", user_schema_long_response
)
login_history_schema = api.model("LoginHistorySchema", login_history_schema)
change_password_schema = api.model(
    "ChangePasswordSchema",
    change_password_schema)

responses_tokens = api.model("ResponsesTokens", responses_tokens)
parser = reqparse.RequestParser()


parser.add_argument("page", type=int, default=0, help="page")
parser.add_argument(
    "per_page",
    type=int,
    default=settings.PAGE_LIMIT_HISTORY,
    help="Items per page")


@api.route("/refresh")
class Refresh(Resource):
    @auth_service.verify_token(refresh=True)
    @api.response(int(HTTPStatus.UNAUTHORIZED),
                  "Token is not corrected\n" "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY),
                  "Token is not corrected\n")
    @api.marshal_with(responses_tokens, code=int(HTTPStatus.OK))
    def post(self):
        jwt = get_jwt()
        result = auth_service.refresh_token(jwt)
        return result, 200


@api.route("/me")
class Me(Resource):
    @auth_service.verify_token()
    @api.response(int(HTTPStatus.UNAUTHORIZED),
                  "Token is not corrected\n" "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY),
                  "Token is not corrected\n")
    @api.marshal_with(user_schema_long_response, code=int(HTTPStatus.OK))
    def get(self):
        jwt = get_jwt()
        user_id = jwt["sub"]
        result = user_service.get_detail_user(user_id)
        return result, 200


@api.route("/change_password")
class ChangePassword(Resource):
    @auth_service.verify_token()
    @api.response(int(HTTPStatus.UNAUTHORIZED),
                  "Token is not corrected\n" "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY),
                  "Token is not corrected\n")
    @api.response(
        int(HTTPStatus.CONFLICT), "New passwords dont matches \n" "Wrong old password"
    )
    @api.response(int(HTTPStatus.BAD_REQUEST), "Wrong user")
    @api.expect(change_password_schema)
    def patch(self):
        jwt = get_jwt()
        user_id = jwt["sub"]
        auth_service.change_password(api.payload, user_id)
        return {"message": "Password changed"}, 200


@api.route("/login_history")
class LoginHistory(Resource):
    @auth_service.verify_token()
    @api.expect(parser)
    @api.response(int(HTTPStatus.UNAUTHORIZED),
                  "Token is not corrected\n" "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY),
                  "Token is not corrected\n")
    @api.marshal_list_with(login_history_schema, code=int(HTTPStatus.OK))
    def get(self):
        jwt = get_jwt()
        user_id = jwt["sub"]
        body = parser.parse_args()
        result = user_service.get_login_history(user_id, body)
        return result, 200


# https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/#revoking-refresh-tokens
@api.route("/logout")
class Logout(Resource):
    @auth_service.verify_token(verify_type=False)
    @api.response(
        int(HTTPStatus.NO_CONTENT), "Access token is exist\n" "Refresh token is exist"
    )
    @api.response(int(HTTPStatus.UNAUTHORIZED),
                  "Token is not corrected\n" "No token")
    @api.response(int(HTTPStatus.UNPROCESSABLE_ENTITY),
                  "Token is not corrected\n")
    def delete(self):
        jwt = get_jwt()
        jti = jwt["jti"]
        ttype = jwt["type"]
        result = auth_service.logout_user(jti, ttype)
        return result, 204

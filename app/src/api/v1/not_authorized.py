from flask_restx import Namespace, Resource, reqparse
from flask_restx._http import HTTPStatus

from db.redis import limiter
from schemas.token import responses_tokens
from schemas.user import (user_schema_login, user_schema_register,
                          user_schema_response)
from services.auth import auth_service
from services.oauth import get_oauth_service

api = Namespace(
    "API для сайта и личного кабинета. Анонимные пользователи", validate=True
)

user_schema_register = api.model("UserSchemaRegister", user_schema_register)
user_schema_login = api.model("UserSchemaLogin", user_schema_login)
user_schema_response = api.model("UserSchemaResponse", user_schema_response)
responses_tokens = api.model("ResponsesTokens", responses_tokens)

parser = reqparse.RequestParser()
parser.add_argument("User-Agent", location="headers")
parser.add_argument("provider", location="args")



@api.route("/register")
class Register(Resource):
    @api.expect(user_schema_register)
    @api.marshal_with(user_schema_response, code=int(HTTPStatus.CREATED))
    @api.response(
        int(HTTPStatus.CONFLICT), "Passwords dont match \n" "Username already exits"
    )
    @api.response(int(HTTPStatus.BAD_REQUEST), "Bad request")
    def post(self):
        result = auth_service.create_user(api.payload)
        return result, 201


@api.route("/login")
class Login(Resource):
    @api.expect(user_schema_login)
    @api.marshal_with(responses_tokens, code=int(HTTPStatus.OK))
    @api.response(int(HTTPStatus.UNAUTHORIZED), "Wrong login or password")
    def post(self):
        user_agent = parser.parse_args()["User-Agent"]
        result = auth_service.login_user(api.payload, user_agent)
        return result, 200


@api.route("/identity/login/<provider>")
class IdentityLogin(Resource):
    @api.response(int(HTTPStatus.TEMPORARY_REDIRECT), "Temporary Redirect")
    def get(self, provider):
        oauth_client = get_oauth_service(provider)
        return oauth_client.redirect_to_provider(provider)


@api.route("/identity/authorization")
class IdentityAuthorization(Resource):
    @api.marshal_with(responses_tokens, code=int(HTTPStatus.OK))
    def get(self):
        provider = parser.parse_args()["provider"]
        user_agent = parser.parse_args()["User-Agent"]
        oauth_client = get_oauth_service(provider)
        username, social_id = oauth_client.get_data_from_provider()
        tokens = oauth_client.authorization_user(user_agent, username, social_id)
        return tokens

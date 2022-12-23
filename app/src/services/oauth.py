from functools import lru_cache
import string
from secrets import choice as secrets_choice
from abc import abstractmethod

from authlib.integrations.flask_client import OAuth
from flask import url_for
from sqlalchemy.exc import NoResultFound
from flask_restx import abort
from flask_restx._http import HTTPStatus

from db.postgres import db
from core.config import settings
from services.auth import auth_service
from models.user import SocialAccount

oauth = OAuth()


class OauthService:
    def __init__(self,
                 name: str,
                 client_id: str,
                 client_secret: str,
                 access_token_url: str,
                 authorize_url: str,
                 userinfo_endpoint: str,
                 client_kwargs: dict):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = access_token_url
        self.authorize_url = authorize_url
        self.userinfo_endpoint = userinfo_endpoint
        self.client_kwargs = client_kwargs
        self.client = self.create_client()
        self.redirect_url = settings.OAUTH_REDIRECT_URL

    def create_client(self):
        oauth.register(
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token_url=self.access_token_url,
            authorize_url=self.authorize_url,
            response_type="code",
            userinfo_endpoint=self.userinfo_endpoint,
            client_kwargs=self.client_kwargs,
        )
        return oauth.create_client(self.name)

    def redirect_to_provider(self, provider):
        return self.client.authorize_redirect(f'{self.redirect_url}?provider={provider}')

    def get_tokens_auth(self):
        return self.client.authorize_access_token()

    def get_user_info(self):
        return self.client.userinfo()

    def check_social_acc(self, social_id):
        try:
            user = db.session.execute(
                db.select(SocialAccount).filter_by(social_id=social_id,
                                                   social_name=self.name)
            ).one()
            return user[0]
        except NoResultFound:
            return False

    @abstractmethod
    def authorization_user(self, user_agent):
        pass

    @staticmethod
    def generate_random_string():
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(10))

    def create_user_body(self, username):
        password = self.generate_random_string()
        return {
            'username': username,
            'password1': password,
            'password2': password
        }


class YandexOauthService(OauthService):
    def authorization_user(self, user_agent):
        self.get_tokens_auth()
        user = self.get_user_info()
        username = user['login']
        social_id = user['id']
        social_acc = self.check_social_acc(social_id)
        if not social_acc:
            user_body = self.create_user_body(username)
            new_user = auth_service.create_user(user_body)
            auth_service.create_record_history(new_user.id, user_agent)
            social_acc = SocialAccount(
                user_id=new_user.id,
                social_id=social_id,
                social_name=self.name
            )
            db.session.add(social_acc)
            db.session.commit()
            tokens = auth_service.create_tokens(str(new_user.id))
            return tokens
        else:
            auth_service.create_record_history(social_acc.user_id, user_agent)
            tokens = auth_service.create_tokens(str(social_acc.user_id))
            return tokens


@lru_cache()
def get_oauth_service(provider):
    match provider:
        case 'yandex':
            return YandexOauthService(
                name='yandex',
                client_id=settings.YANDEX_OAUTH_CLIENT_ID,
                client_secret=settings.YANDEX_OAUTH_CLIENT_SECRET,
                access_token_url=settings.YANDEX_OAUTH_ACCESS_TOKEN_URL,
                authorize_url=settings.YANDEX_OAUTH_AUTHORIZE_URL,
                userinfo_endpoint=settings.YANDEX_OAUTH_USERINFO_ENDPOINT,
                client_kwargs=settings.YANDEX_OAUTH_CLIENT_KWARGS
            )

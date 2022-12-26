from functools import lru_cache
import string
from secrets import choice as secrets_choice
from abc import abstractmethod

from authlib.integrations.flask_client import OAuth
from sqlalchemy.exc import NoResultFound

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
        return self.client.authorize_redirect(
            f'{self.redirect_url}?provider={provider}')

    def get_tokens_auth(self, **kwargs):
        return self.client.authorize_access_token(**kwargs)

    def get_user_info(self):
        return self.client.userinfo()

    def check_social_acc(self, social_id):
        try:
            user = db.session.execute(
                db.select(SocialAccount).filter_by(social_id=str(social_id),
                                                   social_name=str(self.name))
            ).one()
            return user[0]
        except NoResultFound:
            return False

    @abstractmethod
    def get_data_from_provider(self):
        pass

    @staticmethod
    def generate_random_string(len: int):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(len))

    def create_user_body(self, username):
        username = username + self.generate_random_string(5)
        password = self.generate_random_string(10)
        return {
            'username': username,
            'password1': password,
            'password2': password
        }

    def authorization_user(self, user_agent, username, social_id):
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


class YandexOauthService(OauthService):
    def get_data_from_provider(self):
        self.get_tokens_auth()
        user = self.get_user_info()
        username = user['login']
        social_id = user['id']
        return username, social_id


class VkOauthService(OauthService):
    def get_data_from_provider(self):
        data = self.get_tokens_auth(client_id=self.client_id,
                                    client_secret=self.client_secret)
        username = data['email']
        social_id = data['user_id']
        return username, social_id


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
        case 'vk':
            return VkOauthService(
                name='vk',
                client_id=settings.VK_OAUTH_CLIENT_ID,
                client_secret=settings.VK_OAUTH_CLIENT_SECRET,
                access_token_url=settings.VK_OAUTH_ACCESS_TOKEN_URL,
                authorize_url=settings.VK_OAUTH_AUTHORIZE_URL,
                userinfo_endpoint=settings.VK_OAUTH_USERINFO_ENDPOINT,
                client_kwargs=settings.VK_OAUTH_CLIENT_KWARGS
            )

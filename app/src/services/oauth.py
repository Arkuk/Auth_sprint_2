import string
from secrets import choice as secrets_choice

from authlib.integrations.flask_client import OAuth
from flask import url_for
from sqlalchemy.exc import NoResultFound

from db.postgres import db
from core.config import settings
from services.auth import auth_service
from models.user import SocialAccount

oauth = OAuth()


class BaseClassOauth:
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

    def redirect_to_provider(self):
        redirect_uri = url_for(self.redirect_url, _external=True)
        return self.client.authorize_redirect(redirect_uri)

    def get_tokens_auth(self):
        return self.client.authorize_access_token()

    def get_user_info(self):
        return self.client.userinfo()

    @staticmethod
    def check_social_acc(social_id):
        try:
            user = db.session.execute(
                db.select(SocialAccount).filter_by(social_id=social_id)
            ).one()
            return user[0]
        except NoResultFound:
            return False

    def register_user(self):
        user = self.get_user_info()
        print(user)

    @staticmethod
    def generate_random_string():
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(10))





import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Settings(object):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql:"
        f'//{os.getenv("AUTH_POSTGRES_USER")}:'
        f'{os.getenv("AUTH_POSTGRES_PASSWORD")}@'
        f'{os.getenv("AUTH_POSTGRES_HOST")}:{os.getenv("AUTH_POSTGRES_PORT")}/'
        f'{os.getenv("AUTH_POSTGRES_NAME")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = "headers"
    JWT_SECRET_KEY = "super-secret"  # Change this!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    RESTX_MASK_SWAGGER = False
    PAGE_LIMIT_HISTORY = 10
    SECRET_KEY = 'zima-holoda' # Change this!
    OAUTH_REDIRECT_URL = 'http://localhost/api/v1/identity/authorization'

    # yandex oauth
    YANDEX_OAUTH_CLIENT_ID = os.getenv("YANDEX_OAUTH_CLIENT_ID")
    YANDEX_OAUTH_CLIENT_SECRET = os.getenv("YANDEX_OAUTH_CLIENT_SECRET")
    YANDEX_OAUTH_ACCESS_TOKEN_URL = 'https://oauth.yandex.ru/token'
    YANDEX_OAUTH_AUTHORIZE_URL = 'https://oauth.yandex.ru/authorize'
    YANDEX_OAUTH_USERINFO_ENDPOINT = 'https://login.yandex.ru/info'
    YANDEX_OAUTH_CLIENT_KWARGS = {'scope': 'login:info login:email'}


    # vk oauth
    VK_OAUTH_CLIENT_ID = os.getenv("VK_OAUTH_CLIENT_ID")
    VK_OAUTH_CLIENT_SECRET = os.getenv("VK_OAUTH_CLIENT_SECRET")
    VK_OAUTH_ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token'
    VK_OAUTH_AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
    VK_OAUTH_USERINFO_ENDPOINT = 'https://api.vk.com/method/'
    VK_OAUTH_CLIENT_KWARGS = {'scope': 'email'}

settings = Settings()

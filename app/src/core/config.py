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


settings = Settings()

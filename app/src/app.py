import logging

import click
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from passlib.hash import argon2

from services.oauth import oauth
from api import api
from core.jaeger import init_jaeger
from core.config import settings
from db.postgres import db
from db.redis import limiter
from db.redis import jwt_redis_blocklist
from sqlalchemy.exc import NoResultFound
from models.role import Role
from models.user import (User,
                         SocialAccount)
from models.user_login_history import UserLoginHistory
from models.user_role import user_role


def create_app(config=None):
    app = Flask(__name__)
    # инициализация oauth
    oauth.init_app(app)
    # загрузка настроек для Flask
    app.config.from_object("core.config.Settings")
    # батарейка для миграций
    migrate = Migrate(app, db)
    # инициализация дб
    db.init_app(app)
    # инициализация рест апи
    api.init_app(app)
    # инициализация jwt
    jwt = JWTManager(app)

    if settings.DEBUG:
        # ratelimit
        limiter.init_app(app)
        # tracer
        init_jaeger(app)

        @app.before_request
        def before_request():
            request_id = request.headers.get('X-Request-Id')
            if not request_id:
                raise RuntimeError('request id is required')

    @app.cli.command("create-roles")
    def create_roles():
        roles = ("admin", "user", "subscriber")
        for role in roles:
            try:
                db.session.execute(db.select(Role).filter_by(name=role)).one()
                logging.warning(f'role {role} is exists')
            except NoResultFound:
                db.session.add(Role(name=role))
                db.session.commit()

    @app.cli.command("createsuperuser")
    @click.argument(
        "username",
    )
    @click.argument("password")
    def create_superuser(username, password):
        try:
            db.session.execute(db.select(User).filter_by(username='admin')).one()
            logging.warning('admin is exists')
        except NoResultFound:
            admin_role_id = db.session.execute(
                db.select(Role).filter_by(name='admin')
            ).one()
            new_user = User(
                username=username,
                password=argon2.using(rounds=4).hash(password),
                roles=list(admin_role_id),
            )

            db.session.add(new_user)
            db.session.commit()

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    # https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims/?highlight=create_access_token#storing-additional-data-in-jwts
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        user = db.session.execute(db.select(User).filter_by(id=identity)).one()
        roles = [role.name for role in user[0].roles]
        return {
            "roles": roles,
        }

    return app


app = create_app()

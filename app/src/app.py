import click
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from passlib.hash import argon2

from services.oauth import oauth
from api import api
from db.postgres import db
from db.redis import jwt_redis_blocklist
from db.redis import limiter
from models.role import Role
from models.user import (User,
                         SocialAccount)
from models.user_login_history import UserLoginHistory
from models.user_role import user_role
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='0.0.0.0',
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

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
    # инициализация rate limit
    limiter.init_app(app)
    #tracer
    configure_tracer()
    FlaskInstrumentor().instrument_app(app)




    @app.cli.command("create-roles")
    def create_roles():
        roles = ("admin", "user", "subscriber")
        for role in roles:
            db.session.add(Role(name=role))
            db.session.commit()

    @app.cli.command("createsuperuser")
    @click.argument(
        "username",
    )
    @click.argument("password")
    def create_superuser(username, password):
        admin_role_id = db.session.execute(
            db.select(Role).filter_by(name="admin")
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

    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

    return app


app = create_app()

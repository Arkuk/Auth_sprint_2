from datetime import timedelta
from dataclasses import dataclass
from functools import wraps
import logging
from typing import Any

from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, verify_jwt_in_request)
from flask_jwt_extended.exceptions import (NoAuthorizationError,
                                           RevokedTokenError)
from flask_restx import abort
from flask_restx._http import HTTPStatus
from jwt.exceptions import (DecodeError, ExpiredSignatureError,
                            InvalidSignatureError)
from passlib.hash import argon2
from sqlalchemy.exc import NoResultFound

from core.config import settings
from db.postgres import db
from db.redis import jwt_redis_blocklist
from models.user import User
from models.user_login_history import UserLoginHistory


@dataclass
class BodyUserCreate:
    username: str
    password1: str
    password2: str


@dataclass
class BodyUserEdit:
    old_password: str
    new_password1: str
    new_password2: str


@dataclass
class BodyUserLogin:
    username: str
    password: str


class AuthService:
    @staticmethod
    def is_passwords_equal(password1: str, password2: str) -> bool:
        """Сравнение паролей"""
        if password1 == password2:
            return True
        return False

    @staticmethod
    def create_tokens(user_id: str):
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def check_for_id_in_base(user_id: str) -> User | bool:
        try:
            user = db.session.execute(
                db.select(User).filter_by(
                    id=user_id)).one()
            return user[0]
        except NoResultFound:
            return False

    @staticmethod
    def check_for_useername_in_base(username: str) -> User | bool:
        try:
            user = db.session.execute(
                db.select(User).filter_by(username=username)
            ).one()
            return user[0]
        except NoResultFound:
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        return argon2.using(rounds=4).hash(password)

    @staticmethod
    def validate_password(password: str, hash_password: str) -> bool:
        return argon2.verify(password, hash_password)

    def create_user(self, body: dict) -> User | Any:
        body_user_create = BodyUserCreate(**body)
        if self.is_passwords_equal(
                body_user_create.password1, body_user_create.password2):
            if not self.check_for_useername_in_base(body_user_create.username):
                new_user = User(
                    username=body_user_create.username, password=self.hash_password(
                        body_user_create.password1)
                )
                db.session.add(new_user)
                db.session.commit()
                db.session.refresh(new_user)
                return new_user

            else:
                abort(
                    HTTPStatus.CONFLICT,
                    f"Username {body_user_create.username} already exists")
        else:
            abort(HTTPStatus.CONFLICT, "Passwords dont match")

    def change_password(self, body: dict, user_id: str) -> Any:
        body_user_edit = BodyUserEdit(**body)
        user_in_base = self.check_for_id_in_base(user_id)
        if user_in_base:
            hash_password = user_in_base.password
            if self.validate_password(
                    body_user_edit.old_password, hash_password):
                if self.is_passwords_equal(
                        body_user_edit.new_password1, body_user_edit.new_password2):
                    user_in_base.password = self.hash_password(
                        body_user_edit.new_password2)
                    db.session.add(user_in_base)
                    db.session.commit()
                else:
                    abort(HTTPStatus.CONFLICT, "New passwords dont matches")
            else:
                abort(HTTPStatus.CONFLICT, "Wrong old password")
        else:
            abort(HTTPStatus.BAD_REQUEST, "Wrong user")

    @staticmethod
    def create_record_history(user_id: str, user_agent: str) -> bool:
        new_history_record = UserLoginHistory(
            user_id=user_id, user_agent=user_agent)
        db.session.add(new_history_record)
        db.session.commit()
        return True

    def login_user(self, body: dict, user_agent: str) -> dict | Any:
        body_user_login = BodyUserLogin(**body)
        user_in_base = self.check_for_useername_in_base(
            body_user_login.username)
        if user_in_base:
            hash_password = user_in_base.password
            if self.validate_password(body_user_login.password, hash_password):
                self.create_record_history(user_in_base.id, user_agent)
                tokens = self.create_tokens(str(user_in_base.id))
                return tokens
            else:
                abort(HTTPStatus.UNAUTHORIZED, "Wrong login or password")
        else:
            abort(HTTPStatus.UNAUTHORIZED, "Wrong login or password")

    @staticmethod
    def add_token_to_blacklist(jti: str, access_expires: timedelta):
        jwt_redis_blocklist.set(jti, "", ex=access_expires)

    def refresh_token(self, jwt: dict) -> dict:
        user_id = jwt["sub"]
        jti = jwt["jti"]
        tokens = self.create_tokens(user_id)
        self.add_token_to_blacklist(jti, settings.JWT_REFRESH_TOKEN_EXPIRES)
        return tokens

    def logout_user(self, jti: str, ttype: str) -> tuple:
        if ttype == "access":
            self.add_token_to_blacklist(jti, settings.JWT_ACCESS_TOKEN_EXPIRES)
            return {"status": "Access token is exist"}, HTTPStatus.NO_CONTENT
        if ttype == "refresh":
            self.add_token_to_blacklist(
                jti, settings.JWT_REFRESH_TOKEN_EXPIRES)
            return {"status": "Refresh token is exist"}, HTTPStatus.NO_CONTENT

    @staticmethod
    def verify_token(
            optional: bool = False,
            fresh: bool = False,
            refresh: bool = False,
            verify_type: bool = True,
    ):
        """Декоратор для проверки токена и выброса нужного статуса в случае не валидного токена"""

        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                try:
                    token = verify_jwt_in_request(
                        optional=optional,
                        fresh=fresh,
                        refresh=refresh,
                        verify_type=verify_type,
                        locations=["headers"],
                    )
                    if not token:
                        raise NoAuthorizationError
                except RevokedTokenError:
                    abort(HTTPStatus.UNAUTHORIZED, "Token is not corrected")
                except NoAuthorizationError:
                    abort(HTTPStatus.UNAUTHORIZED, "No token")
                except DecodeError:
                    abort(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        "Token is not corrected")
                except InvalidSignatureError:
                    abort(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        "Token is not corrected")
                except ExpiredSignatureError:
                    abort(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        "The token has expired")
                except Exception as e:
                    logging.warning(str(e))
                return fn(*args, **kwargs)

            return decorator

        return wrapper

    @staticmethod
    def func_check_roles(name_roles: list) -> bool | Any:
        name_roles_jwt = get_jwt()["roles"]
        # Пересечение ролей для ручки и ролей в токене
        if list(set(name_roles) & set(name_roles_jwt)):
            return True
        else:
            abort(HTTPStatus.FORBIDDEN, "Permission denied")

    @staticmethod
    def check_roles(name_roles: list[str]):
        """Декоратор для проверки роли"""

        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                name_roles_jwt = get_jwt()["roles"]
                # Пересечение ролей для ручки и ролей в токене
                if list(set(name_roles) & set(name_roles_jwt)):
                    return fn(*args, **kwargs)
                else:
                    abort(HTTPStatus.FORBIDDEN, "Permission denied")

            return decorator

        return wrapper


auth_service = AuthService()

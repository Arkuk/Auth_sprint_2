import http

import pytest
from faker import Faker

from tests.functional.models.user import User
from tests.functional.utils.request import make_request

fake = Faker()

"""user = {
    "username": fake.user_name(),
    "password": fake.password()
}"""

user = {"username": "usertester", "password": "123qWe!"}

user = User(**user)


@pytest.mark.asyncio
async def test_register(client_session):
    """регистрация"""
    response = await make_request(
        client_session,
        endpoint="/register",
        http_method="post",
        data={
            "username": user.username,
            "password1": user.password,
            "password2": user.password,
        },
    )
    assert response.status == http.HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_login(client_session):
    """вход в аккаунт"""
    response = await make_request(
        client_session,
        endpoint="/login",
        http_method="post",
        data={
            "username": user.username,
            "password": user.password,
        },
    )
    assert response.status == http.HTTPStatus.OK
    user.access_token = response.body["access_token"]
    user.refresh_token = response.body["refresh_token"]


@pytest.mark.asyncio
async def test_login_wrongpassword(client_session):
    """проверка сценария, при котором пользователь ввел неверный пароль"""
    response = await make_request(
        client_session,
        endpoint="/login",
        http_method="post",
        data={
            "username": user.username,
            "password": "123!",
        },
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_token_refresh(client_session):
    """проверка получения refresh token"""
    response = await make_request(
        client_session,
        endpoint="/refresh",
        http_method="post",
        headers={"Authorization": f"Bearer {user.refresh_token}"},
    )
    assert response.status == http.HTTPStatus.OK
    user.access_token = response.body["access_token"]
    user.refresh_token = response.body["refresh_token"]


@pytest.mark.asyncio
async def test_user_me(client_session):
    """получение информации о юзере по токену"""
    response = await make_request(
        client_session,
        endpoint="/me",
        http_method="get",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_change_password(client_session):
    """изменение пароля"""
    response = await make_request(
        client_session,
        endpoint="/change_password",
        http_method="patch",
        headers={"Authorization": f"Bearer {user.access_token}"},
        data={
            "old_password": user.password,
            "new_password1": "Qwerty1!69",
            "new_password2": "Qwerty1!69",
        },
    )
    assert response.status == http.HTTPStatus.OK
    user.password = "Qwerty1!69"


@pytest.mark.asyncio
async def test_login_history(client_session):
    """просмотр истории входа"""
    response = await make_request(
        client_session,
        endpoint="/login_history",
        http_method="get",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_logout_access_token(client_session):
    """корректность выхода по access"""
    response = await make_request(
        client_session,
        endpoint="/logout",
        http_method="delete",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )
    assert response.status == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_logout_refresh_token(client_session):
    """корректность выхода по refresh"""
    response = await make_request(
        client_session,
        endpoint="/logout",
        http_method="delete",
        headers={"Authorization": f"Bearer {user.refresh_token}"},
    )
    assert response.status == http.HTTPStatus.NO_CONTENT

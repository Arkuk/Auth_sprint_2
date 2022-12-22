import http
import os
import random

import pytest
from dotenv import load_dotenv

from tests.functional.models.role import Role
from tests.functional.models.user import User
from tests.functional.utils.request import make_request

load_dotenv()

user_admin = {
    "username": os.getenv("AUTH_ADMIN_NAME"),
    "password": os.getenv("AUTH_ADMIN_PASSWORD"),
}

user_admin = User(**user_admin)
test_role = Role(name="testrole")
test_user = User


@pytest.mark.asyncio
async def test_login(client_session):
    """вход в аккаунт"""
    response = await make_request(
        client_session,
        endpoint="/login",
        http_method="post",
        data={
            "username": user_admin.username,
            "password": user_admin.password,
        },
    )
    assert response.status == http.HTTPStatus.OK
    user_admin.access_token = response.body["access_token"]
    user_admin.refresh_token = response.body["refresh_token"]


@pytest.mark.asyncio
async def test_get_users(client_session):
    """получение списка пользователей"""
    response = await make_request(
        client_session,
        endpoint="/users",
        http_method="get",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
    )
    test_user.id = random.choice(response.body)["id"]
    assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_roles(client_session):
    """получение списка ролей"""
    response = await make_request(
        client_session,
        endpoint="/roles",
        http_method="get",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_add_role(client_session):
    """добавление новой роли"""
    response = await make_request(
        client_session,
        endpoint="/roles",
        http_method="post",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
        data={"name": test_role.name},
    )
    assert response.status == http.HTTPStatus.CREATED
    test_role.id = response.body.get("id")


@pytest.mark.asyncio
async def test_change_role(client_session):
    """корректность изменения имени роли"""
    test_role.name = "newtestrole"
    response = await make_request(
        client_session,
        endpoint="/roles",
        http_method="put",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
        data={"id": test_role.id, "name": test_role.name},
    )
    assert response.status == http.HTTPStatus.OK
    assert response.body.get("name") == test_role.name


@pytest.mark.asyncio
async def test_add_user_role(client_session):
    """добавление роли пользователю"""
    response = await make_request(
        client_session,
        endpoint=f"/users/{test_user.id}/roles",
        http_method="post",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
        data={"role_id": test_role.id},
    )
    assert response.status == http.HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_get_user_role(client_session):
    """получаем роли пользователя"""
    response = await make_request(
        client_session,
        endpoint=f"/users/{test_user.id}/roles",
        http_method="get",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_discard_user_role(client_session):
    """забираем роль у пользователя"""
    response = await make_request(
        client_session,
        endpoint=f"/users/{test_user.id}/roles",
        http_method="delete",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
        data={"role_id": test_role.id},
    )
    assert response.status == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_role(client_session):
    """удаление роли"""
    response = await make_request(
        client_session,
        endpoint="/roles",
        http_method="delete",
        headers={"Authorization": f"Bearer {user_admin.access_token}"},
        data={"id": test_role.id, "name": test_role.name},
    )
    assert response.status == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_no_access(client_session):
    """на любом методе проверяем корректность проверки прав"""
    response = await make_request(client_session, endpoint="/roles", http_method="get")
    assert response.status == http.HTTPStatus.UNAUTHORIZED

import pytest
from aiohttp import ClientSession


@pytest.fixture(scope="session")
async def client_session(event_loop):
    session = ClientSession()
    yield session
    await session.close()

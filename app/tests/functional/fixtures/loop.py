import asyncio
from asyncio.events import AbstractEventLoop
from typing import Any, Generator

import pytest


@pytest.fixture(scope="session")
async def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

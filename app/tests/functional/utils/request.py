from dataclasses import dataclass
from http.client import HTTPResponse

from multidict import CIMultiDictProxy

from tests.functional.settings import test_settings


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int

async def make_request(
        client_session,
        http_method: str,
        data: dict = {},
        headers: str = None,
        endpoint: str = None,
) -> HTTPResponse:
    dispatcher: dict = {
        "get": client_session.get,
        "post": client_session.post,
        "put": client_session.put,
        "delete": client_session.delete,
        "patch": client_session.patch,
    }
    async with dispatcher.get(http_method)(
            url=f"{test_settings.service_url}/api/v1{endpoint}",
            headers=headers,
            json=data,
    ) as response:
        return HTTPResponse(
            body=await response.json(),
            headers=response.headers,
            status=response.status,
        )

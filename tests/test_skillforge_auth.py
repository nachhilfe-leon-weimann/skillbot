import asyncio
from urllib.parse import parse_qs

import httpx
import pytest
from pydantic import SecretStr
from skillforge_client import Client

from skillbot.core.skillforge.auth import ClientCredentialsAuth
from skillbot.core.skillforge.errors import SkillForgeClientAuthenticationError

BASE_URL = "https://skillforge.test"


def _authenticated_get(token_response: httpx.Response) -> tuple[list[httpx.Request], httpx.Response]:
    """Send one GET through ClientCredentialsAuth, with SkillForge answering the token request as given."""

    token_requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/auth/token":
            token_requests.append(request)
            return token_response
        return httpx.Response(200, json={"authorization": request.headers.get("Authorization")})

    transport = httpx.MockTransport(handle)

    async def run() -> httpx.Response:
        public_client = Client(base_url=BASE_URL).set_async_httpx_client(
            httpx.AsyncClient(base_url=BASE_URL, transport=transport)
        )
        auth = ClientCredentialsAuth(client=public_client, client_id="skillbot", client_secret=SecretStr("s3cret"))
        async with httpx.AsyncClient(base_url=BASE_URL, transport=transport, auth=auth) as http_client:
            try:
                return await http_client.get("/api/v1/crm/parties")
            finally:
                await public_client.get_async_httpx_client().aclose()

    return token_requests, asyncio.run(run())


def test_requests_a_client_credentials_token_and_sends_it_as_bearer() -> None:
    token_requests, response = _authenticated_get(
        httpx.Response(
            200,
            json={"access_token": "token-1", "expires_in": 300, "scope": "crm:read", "token_type": "bearer"},
        )
    )

    assert len(token_requests) == 1
    assert parse_qs(token_requests[0].content.decode()) == {
        "grant_type": ["client_credentials"],
        "client_id": ["skillbot"],
        "client_secret": ["s3cret"],
    }
    assert response.json() == {"authorization": "Bearer token-1"}


def test_rejected_client_credentials_raise_an_authentication_error() -> None:
    with pytest.raises(SkillForgeClientAuthenticationError):
        _authenticated_get(
            httpx.Response(
                401,
                json={"code": "invalid_client", "detail": "The client credentials are invalid."},
            )
        )

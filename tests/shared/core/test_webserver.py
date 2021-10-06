import asyncio
import os
import pytest
from httpx import AsyncClient
from shared.core.webserver import SomeFastApiApp

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def client():
    app = SomeFastApiApp()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_SomeFastApiApp_get_metrics(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert '# HELP' in response.text






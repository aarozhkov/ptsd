import asyncio
import pytest
from httpx import AsyncClient
from supervisor.main import supervisor_api

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def client():
    async with AsyncClient(app=supervisor_api, base_url="http://test") as client:
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

@pytest.mark.asyncio
async def test_SupervisorApi_get_valid_account(client):
    response = await client.get("/account?brand=RC-Commercial")
    assert response.status_code in [200, 404]


import asyncio
import os
import pytest
from httpx import AsyncClient


HOST = "http://localhost:8112"


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def client():
    async with AsyncClient(base_url=HOST) as client:
        yield client


@pytest.fixture(scope='module')
@pytest.mark.asyncio
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_post_test(client):
    payload = {
        'version': 'isString',
        'url': 'http://xxxxx.com',
        'ptdAddress': 'isString',
        'phoneOrEmail': 'xxxx@yyyy.com',
        'extension': 'isString',
        'password': 'isString',
        'testSuite': 'isString',
        'convName': 'isString',
        'targetPartitionUnit': 'partition@unit:10',
        'notifyOnComplete': True,
        'ptrIndex': 500
    }
    resp = await client.post(f'{HOST}/test', json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('ptrTestId')


@pytest.mark.asyncio
async def test_post_invalidate_cache(client):
    resp = await client.post(f'{HOST}/invalidate-cache')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')


@pytest.mark.asyncio
async def test_get_status(client):
    resp = await client.get(f'{HOST}/status')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('app')
    assert data.get('version')


@pytest.mark.asyncio
async def test_post_update(client):
    resp = await client.post(f'{HOST}/update')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')


@pytest.mark.asyncio
async def test_post_test_jsonxml(client):
    payload = {
        'version': 'isString',
        'jsonxml': 'exists',
        'convName': 'isString',
        'notifyOnComplete': True
    }
    resp = await client.post(f'{HOST}/test-jsonxml', json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('ptrTestId')


@pytest.mark.asyncio
async def test_get_tests(client):
    resp = await client.get(f'{HOST}/tests?status=passed')
    data = resp.json()
    # TODO remove? It doesn't use in the main app
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_test_allure(client):
    testId = 100
    resp = await client.get(f'{HOST}/test/{testId}/allure/index.html')
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_test_log(client):
    testId = 100
    resp = await client.get(f'{HOST}/test/{testId}/log')
    assert resp.status_code == 200

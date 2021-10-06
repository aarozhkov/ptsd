import asyncio
import os
import pytest
from httpx import AsyncClient


HOST = "http://localhost:8113"

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def client():
    async with AsyncClient(base_url=HOST) as client:
        yield client

@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_get_metrics(client):
    resp = await client.get('/metrics')
    assert resp.status_code == 200
    assert '# HELP' in resp.text

@pytest.mark.asyncio
async def test_get_status(client):
    resp = await client.get('/status')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('app')
    assert data.get('version')

@pytest.mark.asyncio
async def test_get_status_json(client):
    params = {'groupBy': 'groupByTest', 'status': 'PASSED', 'view': 'all'}
    resp = await client.get('/status-json', params=params)
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('groupBy') == 'groupByTest'
    assert data.get('rcv')

@pytest.mark.asyncio
async def test_post_invalidate_ptr_cache(client):
    resp = await client.post('/invalidate-ptr-cache')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('message') == '/invalidate-cache request have been sent to all PTRs'


@pytest.mark.asyncio
async def test_post_log_level(client):
    payload = {
        'level': 'debug'
    }
    resp = await client.post(f'{HOST}/log-level', data=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert json.get('success')


@pytest.mark.asyncio
async def test_post_test_completed(client):
    payload = {
        'ptrTestId': 100,
        'ptrIndex': 500,
        'outcomes': {
            'status': 'outcome.status',
            'checkName': 'outcome.name',
            'failedReason': 'outcome.reason',
            'callId': 100
        }
    }
    resp = await client.post(f'{HOST}/test-completed', data=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')


@pytest.mark.asyncio
async def test_post_update_ptr(client):
            resp = await client.post(f'{HOST}/update-ptr')
            data = resp.json()
            assert resp.status_code == 200
            assert data.get('success')
            assert data.get(
                'message') == '/update request have been sent to all PTRs'


@pytest.mark.asyncio
async def test_post_update(client):
    resp = await client.post(f'{HOST}/update')
    data = resp.json()
    assert resp.status_code == 200
    assert data.get('success')
    assert data.get('message') == 'The update has been started..'

import asyncio
import pytest
import adapter.main
# from shared.core.adapter import TestRequest

"""
{
  "version": "0.1",
  "url": "https://v.ringcentral.com",
  "ptd_address": "http://iad41-c04-ptd01:4444",
  "phone_or_email": "14706495518",
  "extension": "101",
  "password": "Test!123",
  "test_suite": "video",
  "notify_on_complete": true,
  "test_id": 0
}
"""

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def data():
    data = {
        "version": "0.1",
        "url": "https://v.ringcentral.com",
        "ptd_address": "http://iad41-c04-ptd01:4444",
        "phone_or_email": "14706495518",
        "extension": "101",
        "password": "Test!123",
        "test_suite": "video",
        "notify_on_complete": True,
        "test_id": 0
    }
    yield data

@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest.mark.asyncio
# async def test_execute(data):
    # validTestRequest = TestRequest(data)
    # assert 'RC-Commercial' in accounter.pool.keys()

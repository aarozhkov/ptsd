import asyncio
import pytest
import adapter.main
# from shared.core.adapter import TestRequest

"""
{
  "version": "0.1",
  "url": "https://v.ringcentral.com",
  "ptdAddress": "http://iad41-c04-ptd01:4444",
  "phoneOrEmail": "18887533251",
  "extension": "101-110",
  "password": "123qwe!@#QWE",
  "testSuite": "video",
  "convName": "sjc_1",
  "targetPartitionUnit": "us-01@sjc01:10",
  "notifyOnComplete": true,
  "ptrIndex": 0
}
"""

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def data():
    data = {
        "version": "0.1",
        "url": "https://v.ringcentral.com",
        "ptdAddress": "http://iad41-c04-ptd01:4444",
        "phoneOrEmail": "18887533251",
        "extension": "101-110",
        "password": "123qwe!@#QWE",
        "testSuite": "video",
        "convName": "sjc_1",
        "notifyOnComplete": True,
        "ptrIndex": 0
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

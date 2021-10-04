import os
import aiohttp
import pytest

#HOST = os.environ.get('APP_HOST', f'http://{CONFIG_HOST}:{PORT}')
HOST = "http://localhost:8113"
#HOST = "http://sjc01-c04-ptl01:8113"

async def test_get_metrics():
    async with aiohttp.ClientSession() as session:
        async with session.get('%s/metrics' % HOST) as resp:
            assert resp.status == 200
            # assert await resp.text() == '# HELP'

async def test_get_status():
    async with aiohttp.ClientSession() as session:
        async with session.get('%s/status' % HOST) as resp:
            json = await resp.json()
            assert resp.status == 200
            assert json.get('success')

# {"success":true,"groupBy":"partition.unit.brand.location.test","rcv":{"status":"GRAY"}}
# http://localhost:8113/status-json?groupBy=test&status=PASSED&view=all
async def test_get_status_json():
    async with aiohttp.ClientSession() as session:
        async with session.get('%s/status-json?groupBy=groupByTest&status=PASSED&view=all' % HOST) as resp:
            json = await resp.json()
            assert resp.status == 200
            assert json.get('success')
            assert json.get('groupBy') == 'groupByTest'

async def test_post_invalidate_ptr_cache():
    async with aiohttp.ClientSession() as session:
        async with session.post('%s/invalidate-ptr-cache' % HOST) as resp:
            json = await resp.json()
            assert resp.status == 200
            assert json.get('success')
            assert json.get('message') == '/invalidate-cache request have been sent to all PTRs'

# #Has 500 error response on PTL prod
# async def test_post_log_level():
#     async with aiohttp.ClientSession() as session:
#         payload = {
#             'level': 'debug'
#         }
#         async with session.post('%s/log-level' % HOST, data=payload) as resp:
#             assert resp.status == 200
#             json = await resp.json()
#             assert json.get('success')


# TODO NEED FIXTURES HERE (PTR)
# async def test_post_test_completed():
#     async with aiohttp.ClientSession() as session:
#         payload = {
#             'ptrTestId': 100,
#             'ptrIndex': 500,
#             'outcomes': {
#                 'status': 'RUNNING',
#                 'checkName': 'outcome.name',
#                 'failedReason': 'outcome.reason',
#                 'callId': 11
#             }
#         }
#         async with session.post('%s/test-completed' % HOST, data=payload) as resp:
#             json = await resp.json()
#             assert resp.status == 200
#             assert json.get('success')

async def test_post_update_ptr():
    async with aiohttp.ClientSession() as session:
        async with session.post('%s/update-ptr' % HOST) as resp:
            json = await resp.json()
            assert resp.status == 200
            assert json.get('success')
            assert json.get('message') == '/update request have been sent to all PTRs'

# Restart service (SelfUpdate)
async def test_post_update():
    async with aiohttp.ClientSession() as session:
        async with session.post('%s/update' % HOST) as resp:
            json = await resp.json()
            assert resp.status == 200
            assert json.get('success')
            assert json.get('message') == 'The update has been started..'




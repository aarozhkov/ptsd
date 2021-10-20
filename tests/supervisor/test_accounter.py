import asyncio
import pytest
from supervisor.core.accounter import Accounter
from shared.models.account import Account

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def accounter():
    data =  {'RC-Commercial': [{'phone_or_email': 1470649551, 'extension': [101, 102], 'password': 'Abyrvalg!123'}, {'phone_or_email': 1470649552, 'extension': [103], 'password': 'Abyrvalg!123]'}]}
    accounter = Accounter()
    accounter.parse_model(data)
    yield accounter



@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_get_random_account(accounter):
    account = accounter.get_random_account_for_brand('RC-Commercial')
    assert account.phone_or_email



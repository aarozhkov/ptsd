import asyncio
from typing import Optional, Protocol, List
import logging
from httpx import AsyncClient, HTTPError
from pydantic import ValidationError

from shared.models.account import Account
from prometheus_client import Gauge


ACCOUNTS_STATUS = Gauge(
    "accounts_pool", "Scheduled test task count in queue ", ["brand", "status"]
)

# TODO: alert on changes in summary account(any status) count - it must be same always.


class AccounterException(Exception):
    """Specific account exceptions"""


class Accounteer(Protocol):
    async def book_account(self, brand: str) -> Optional[Account]:
        """Get available account for given brand"""

    async def release_account(self, account: Account):
        """Release booked account"""


class LocalAccounteer:
    """Accounteer with local account configuration"""

    def __init__(
        self, accounts: List[Account], logger: Optional[logging.Logger] = None
    ):
        self.available_accounts: List[Account] = accounts
        self.reserved_accounts: List[Account] = []
        self._init_account_metrics()
        self.log = logger if logger else logging.getLogger(self.__class__.__name__)

        # TODO this variables can be setted as configurable
        self.allocation_attempts = 3
        self.attempt_wait = 2

    def _init_account_metrics(self):
        """On instance init: fill actual accounts state in metrics"""
        # Expected we have only available accounts?
        # TODO: Handle cases: accounteer are reloaded while accounts in work?
        for account in self.available_accounts:
            ACCOUNTS_STATUS.labels(brand=account.brand, status="available").inc()

    def _get_account(self, brand: str) -> Optional[Account]:
        for account in self.available_accounts:
            if account.brand == brand:
                self.reserved_accounts.append(account)
                self.available_accounts.remove(account)
                ACCOUNTS_STATUS.labels(brand=account.brand, status="available").dec()
                ACCOUNTS_STATUS.labels(brand=account.brand, status="reserved").inc()
                return account
        return None

    async def book_account(self, brand: str) -> Optional[Account]:
        """Get available account for given brand.
        Try to get available accounts.
        3 attempts with expenational wait time

        """
        # FIXME probably attempts must be done on clinet side
        for attempt in range(self.allocation_attempts):
            account = self._get_account(brand)
            if account:
                return account
            await asyncio.sleep(self.attempt_wait * attempt)
        self.log.error(
            "Fails to allocate account for %s in %s seconds",
            brand,
            self.allocation_attempts * self.attempt_wait,
        )
        return None

    async def release_account(self, account: Account):
        """Release booked account"""

        if account in self.reserved_accounts:
            if account not in self.available_accounts:
                self.available_accounts.append(account)
                ACCOUNTS_STATUS.labels(brand=account.brand, status="available").inc()
            else:
                self.log.error(
                    "Release account: account exists in available and reserved pools. acc: %s",
                    account,
                )
            self.reserved_accounts.remove(account)
            ACCOUNTS_STATUS.labels(brand=account.brand, status="reserved").dec()
            self.log.info("Account released: %s", account)
            return
        if account in self.available_accounts:
            # In case of Timer release. OR accounter restart
            self.log.debug("Release: account was available before. acc: %s", account)
            return

        # FIXME Should handle this somehow. Should we add account in to pool?
        self.log.error("Did not found account in both pools. acc: %s", account)
        return


class RemoteAccounteer:
    """Fetch accounts from remote accounteer"""

    def __init__(self, remote_accounteer_url: str, logger: logging.Logger):
        # Assume url validation was done on higher level
        self.remote_url = remote_accounteer_url
        self.log = logger if logger else logging.getLogger(self.__class__.__name__)

        self.allocation_attempts = 3
        self.attempt_wait = 2

    async def book_account(self, brand: str) -> Optional[Account]:
        # TODO:
        # IF remote accounter hase Retry logic and we will retry: start test run time will be extended
        # How match retry we need here?
        attempts = 3
        # FIXME can make http client with pydantic schema validation?
        async with AsyncClient() as client:
            while attempts > 0:
                try:
                    r = await client.get(
                        f"{self.remote_url}/api/v1/account?brand={brand}"
                    )
                    r.raise_for_status()
                    self.log.debug(
                        "Get data from remote accounteer: %s, acc: %s",
                        self.remote_url,
                        r.json(),
                    )
                    account = Account.parse_obj(r.json())
                    return account
                except ValidationError as e:
                    self.log.exception(
                        "Got issues validating data from remote accounteer: %s", e
                    )
                    return None
                except HTTPError as e:
                    self.log.exception(
                        "Got RequestError: %s, will retry in 1 second",
                        e,
                    )
                    await asyncio.sleep(1)
                    attempts += 1
        self.log.error("Fails all attempts to book account remotely. Brand %s", brand)
        return None

    async def release_account(self, account: Account):
        """Release booked account"""
        attempts = 3
        async with AsyncClient() as client:
            while attempts > 0:
                try:
                    r = await client.post(
                        f"{self.remote_url}/api/v1/release", json=account.json()
                    )
                    r.raise_for_status()
                    return
                except HTTPError as e:
                    # FIXME: drop attempts for 4xx.
                    self.log.exception(
                        "Got HTTPError: %s, will retry in 1 second",
                        e,
                    )
                    await asyncio.sleep(1)
                    attempts += 1
        self.log.error("Fails all attempts to release account remotely.")
        return

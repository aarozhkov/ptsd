import re
import httpx

# from functools import lru_cache


class VersionCheckException(Exception):
    """Specific Exceptions"""


class VersionChecker:
    """RWC cersion grabber with Result cacheing"""

    dependancies_url_template = r'src="(\/static\/dependencies.+?)"'
    version_tempate = r'"r_(.+?)"'
    cache = {}
    max_hits = 20  # FIXME - Hardcoded config

    async def get_version(self, brand_endpoint: str) -> str:
        """Result cacheing implementation"""
        brand_cached = self.cache.get(brand_endpoint, None)

        if brand_cached and brand_cached["hit_count"] <= self.max_hits:
            self.cache[brand_endpoint]["hit_count"] += 1
            return brand_cached["value"]

        result = await self.get_version_asyncly(brand_endpoint)
        self.cache[brand_endpoint] = {"hit_count": 1, "value": result}

        print(self.cache)
        return result

    async def get_version_asyncly(self, brand_endpoint: str) -> str:
        async with httpx.AsyncClient() as client:
            index_html = await client.get(brand_endpoint)
            dependancy_url = re.search(self.dependancies_url_template, index_html.text)
            if not dependancy_url:
                raise VersionCheckException(
                    "Cant find dependancy static url within: ", brand_endpoint
                )
            dependancy_js = await client.get(brand_endpoint + dependancy_url.group(1))
            version = re.search(self.version_tempate, dependancy_js.text)
            if not version:
                raise VersionCheckException(
                    "Cant find version within: ",
                    brand_endpoint,
                    dependancy_url.group(1),
                )
            return version.group(1)

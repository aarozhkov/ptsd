import re
import httpx

# from functools import lru_cache


class VersionCheckException(Exception):
    """Specific Exceptions"""


class VersionChecker:
    dependancies_url_template = r'src="(\/static\/dependencies.+?)"'
    version_tempate = r'"r_(.+?)"'

    # @lru_cache(maxsize=32)  - FIXME it is not work for async code
    async def get_version(self, brand_endpoint: str) -> str:
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

# Service implements test scheduler entity
# TODO: impelemnt simple scheduler on top
from asyncio import Queue, create_task
from typing import List


class GenericQperLoc:
    def __init__(self, locations: List[str], max_len=100):
        self.queues_map = self._create_queues(locations, max_len)

    @classmethod
    def _create_queues(cls, locations, max_len):
        return {location: Queue(maxsize=max_len) for location in locations}

    async def push(self, location: str, task: str):
        if location not in self.queues_map.keys():
            raise KeyError("No queue for this location")
        await self.queues_map[location].put(task)

    async def get(self, location: str) -> str:
        if location not in self.queues_map.keys():
            raise KeyError("No queue for this location")
        return await self.queues_map[location].get()


class GenericQ:
    def __init__(self, max_len=100):
        self.queues_map = self._create_queues(max_len)

    @classmethod
    def _create_queues(cls, max_len):
        return Queue(maxsize=max_len)

    async def push(self, location: str, task: str):
        location = 0  # just to check
        await self.queues_map.put(task)

    async def get(self, location: str) -> str:
        location = 0
        return await self.queues_map.get()


class Scheduler:
    def __init__(self, queue, locations, brands):
        self.q = queue
        self.bucket = self.create_bucket(brands)
        self.locations = locations

    def create_bucket(self, brands: dict):
        """will return list of tuples (brand, location)"""
        result = []
        for brand in brands:
            for _ in range(brands[brand]["unitsCount"]):
                result.append(brand)
        return result

    def _add_pusher(self, location):
        create_task(self.pusher(location), name=f"{location}-writer")

    def run(self):
        for location in self.locations:
            self._add_pusher(location)

    def get_randomly(self):
        num = random.random() * len(self.bucket)
        return self.bucket[int(num)]

    async def pusher(self, location):
        while True:
            await self.q.push(location, self.get_randomly())

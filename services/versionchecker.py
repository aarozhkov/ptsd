# Service witch will check all Brand endpoints and collect versions.
# TODO: service should know about available Java test builds
# TODO: There should be allert on required test miss? Or it should be from PTR/PTD?


import asyncio

# from fastapi import APIRouter


class VersionChecker:
    def __init__(self, value: int = 0):
        self.value = value
        # TODO define params

    def set_value(self, value):
        self.value = value
        return True

    def get_value(self):
        return self.value

    async def run(self):
        while True:
            await asyncio.sleep(5)
            print("runned")
            self.value += 1


# router = APIRouter(
#     prefix="/versionchecker",
#     tags=['versionchecker']
# )

# @router.on_event("startup")
# async def run_value_inc():
#     vc = VersionChecker()
#     asyncio.create_task(vc.run())

# @router.get('/versions')
# def get_version():
#     return {"version": vc.get_value()}

# @router.post('/versions')
# def set_version(version: int):
#     print(item)
#     if vc.set_value(version):
#         return {"success": True, "version": vc.get_value()}
#     else:
#         return {"success": False}
version_checker = VersionChecker(1)

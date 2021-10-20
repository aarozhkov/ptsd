import uvicorn
from shared.core.webserver import SomeFastApiApp
from supervisor.api.v1.endpoints import supervisor_router


class SupervisorApi(SomeFastApiApp):
    def __init__(self, app_name="supervisor"):
        super(SupervisorApi, self).__init__(app_name=app_name)
        self.include_router(supervisor_router)



if __name__=='__main__':
    supervisor_api = SupervisorApi()
    uvicorn.run(supervisor_api, host="0.0.0.0", port=8113)


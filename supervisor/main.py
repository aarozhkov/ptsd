import uvicorn
from supervisor.api.supervisor_api import SupervisorApi



supervisor_api = SupervisorApi(app_name="supervisor")



if __name__=='__main__':
    uvicorn.run(supervisor_api, host="0.0.0.0", port=8113)


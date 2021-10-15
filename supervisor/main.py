import uvicorn
from shared.core.webserver import SomeFastApiApp



supervisor_api = SomeFastApiApp(app_name="supervisor")


if __name__=='__main__':
    uvicorn.run(supervisor_api, host="0.0.0.0", port=8113)


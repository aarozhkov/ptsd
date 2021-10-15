import uvicorn
from fastapi import Response
from fastapi.responses import JSONResponse

from xmljson import badgerfish as bf
from shared.core.webserver import SomeFastApiApp
from shared.core.adapter import TestRequest
from adapter.core import selenium_template, config

adapter_api = SomeFastApiApp(app_name="adapter")
parser = config.AdapterConfigParser()
config = parser.parse("adapter/adapter.yaml")

@adapter_api.get("/status")
async def adapter_status():
    return {
        "success": True,
        "app": "ptsd_adapter",
        "version": "v0.1"
    }

@adapter_api.post("/test")
async def checkAndRun(data: TestRequest):
    try:
        push = selenium_template.initTestNg(data, config)
        return {
            "success": True,
            "ptrTestId": push.ptrIndex
        }
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )


@adapter_api.post("/testxml")
async def checkAndRun(data: TestRequest):
    try:
        push = selenium_template.initTestNg(data, config)
        return Response(push, media_type="application/xml")
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )

if __name__ == '__main__':
    uvicorn.run(adapter_api, host="0.0.0.0", port=8112)

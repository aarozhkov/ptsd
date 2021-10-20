import uvicorn
from fastapi import Response
from fastapi.responses import JSONResponse

from shared.core.webserver import SomeFastApiApp
from shared.models.adapter import TestRequest
from adapter.core import adapter

adapter_api = SomeFastApiApp(app_name="adapter")
parser = adapter.AdapterConfigParser()
adapter = adapter.Adapter()
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
        XML = adapter.initTestNg(data, config)
        adapter.startPipeline(XML)
        
        return {
            "success": True,
            "ptrTestId": 0
        }
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )


@adapter_api.post("/testxml")
async def checkAndRunXML(data: TestRequest):
    try:
        XML = adapter.initTestNg(data, config)
        adapter.startPipeline(XML)
        push = "yeap"
        return Response(push, media_type="application/xml")
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )

if __name__ == '__main__':
    uvicorn.run(adapter_api, host="0.0.0.0", port=8112)

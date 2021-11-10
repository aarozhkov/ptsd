import uvicorn
from fastapi import BackgroundTasks, Response
from fastapi.responses import JSONResponse
from shared.core.webserver import SomeFastApiApp
from shared.models.adapter import TestRequest
from shared.core.yamlparser import YamlParser

from adapter.core import adapter

adapter_api = SomeFastApiApp(app_name="adapter")
adapter = adapter.Adapter()
parser = YamlParser()
config = parser.parse("adapter/adapter.yaml")

@adapter_api.get("/status")
async def adapter_status():
    return {"success": True, "app": "ptsd_adapter", "version": "v0.1"}


@adapter_api.post("/test")
async def checkAndRun(data: TestRequest, background_tasks: BackgroundTasks):
    try:
        XML = adapter.initTestNg(data, config)
        testId = adapter.prepareDirectory(XML, data, config)
        background_tasks.add_task(adapter.startPipeline, testId, config)
        return JSONResponse(status_code=418, content={"success": True, "ptrTestId": testId})
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )


@adapter_api.post("/testxml")
async def checkAndRunXML(data: TestRequest, background_tasks: BackgroundTasks):
    try:
        XML = adapter.initTestNg(data, config)
        testId = adapter.prepareDirectory(XML, data, config)
        background_tasks.add_task(adapter.startPipeline, testId, config)
        return Response(XML, media_type="application/xml")
    except:
        return JSONResponse(
            status_code=418,
            content={"success": False},
        )


if __name__ == "__main__":
    uvicorn.run(adapter_api, host="0.0.0.0", port=8112)

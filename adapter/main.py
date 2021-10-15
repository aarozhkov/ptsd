import uvicorn
from fastapi import Response

from xmljson import badgerfish as bf
from shared.core.webserver import SomeFastApiApp
from shared.core.adapter import TestRequest
from adapter.core import selenium_template
from adapter.core import config

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
    classes = config["testSuites"][data.testSuite]
    push = selenium_template.initTestNg(data, classes)
    return Response(push, media_type="application/xml")
    # return {
    #     "success": True,
    #     "ptrTestId": data.ptrIndex
    # }


if __name__ == '__main__':
    uvicorn.run(adapter_api, host="0.0.0.0", port=8112)

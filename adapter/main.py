import uvicorn
from fastapi import Response

from xmljson import badgerfish as bf
from shared.core.webserver import SomeFastApiApp
from shared.core.adapter import TestRequest
from adapter.core import selenium_template

adapter_api = SomeFastApiApp(app_name="adapter")


@adapter_api.get("/status")
async def adapter_status():
    return {
        "success": True,
        "app": "ptsd_adapter",
        "version": "v0.1"
    }

@adapter_api.post("/test")
async def checkAndRun(data: TestRequest):
    return Response(content=bf.etree(selenium_template.initTestNgJson(data, "testclasses")), media_type="application/xml")
    # return {
    #     "success": True,
    #     "ptrTestId": data.ptrIndex
    # }

if __name__ == '__main__':
    uvicorn.run(adapter_api, host="0.0.0.0", port=8112)

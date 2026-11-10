from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root_handler(request: Request):
    return JSONResponse({
        "message": "HELLO FROM ROOT",
        "url": str(request.url),
        "query": dict(request.query_params),
        "headers": dict(request.headers)
    })

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, full_path: str):
    return JSONResponse({
        "full_path": full_path,
        "url_path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers)
    })

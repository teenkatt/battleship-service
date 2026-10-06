from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from battleship.routes import router
from battleship.storage import SessionFinished

app = FastAPI(title="Battleship game service")


@app.middleware("http")
async def catch_unexpected_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.exception_handler(SessionFinished)
async def session_finished(request: Request, exc: SessionFinished):
    return JSONResponse(status_code=410, content={"detail": "Session is finished"})


@app.exception_handler(RequestValidationError)
async def bad_request(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Bad Request"})


@app.get("/ping")
def ping():
    return {"ping": "pong"}


app.include_router(router)

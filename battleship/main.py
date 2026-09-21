from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from battleship.routes import router

app = FastAPI(title="Battleship game service")


@app.middleware("http")
async def catch_unexpected_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/ping")
def ping():
    return {"ping": "pong"}


app.include_router(router)

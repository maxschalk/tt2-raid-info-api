from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .routers import main

app = FastAPI()

app.include_router(main.router)


@app.get("/")
async def root():
    return RedirectResponse("/docs")

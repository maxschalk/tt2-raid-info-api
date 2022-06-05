from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .routers import main

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})

app.include_router(main.router)


@app.get("/")
async def root():
    return RedirectResponse("/docs")

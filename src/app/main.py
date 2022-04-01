from fastapi import FastAPI

from routers import raw_seeds

app = FastAPI()

app.include_router(raw_seeds.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

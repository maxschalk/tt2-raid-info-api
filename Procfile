web: waitress-serve --port=$PORT src.app.main:app
old: gunicorn -w 3 -k uvicorn.workers.UvicornWorker src.app.main:app

call .\venv\Scripts\activate.bat

gunicorn src.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
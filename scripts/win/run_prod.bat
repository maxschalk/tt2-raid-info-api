
call .\venv\Scripts\activate.bat

uvicorn src.app.main:app --host 0.0.0.0 --port 80
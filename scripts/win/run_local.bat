
call .\venv\Scripts\activate.bat

uvicorn src.app.main:app --host 0.0.0.0 --port 5000 --reload
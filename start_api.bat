@echo off
rem --- SageMind Tech Services API Server Startup (Windows) ---

rem Ensure the virtual environment is active before starting
call venv\Scripts\activate

echo ================================================
echo  Starting SageMind Tech Services API Server...
echo ================================================
echo Access the dashboard at: http://127.0.0.1:8000
echo Access the API docs at:  http://127.0.0.1:8000/docs
echo ------------------------------------------------

rem The standard command to run FastAPI application with auto-reload
python -m uvicorn app.main:app --reload --port 8000

rem Deactivate virtual environment when the server stops
deactivate

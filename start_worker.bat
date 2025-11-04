@echo off
rem --- SageMind Tech Services Background Worker Startup (Windows) ---

rem Ensure the virtual environment is active before starting
call venv\Scripts\activate

echo ================================================
echo  Starting SageMind Tech Services Worker...
echo ================================================
echo This process handles all background scraping and price alerts.
echo Keep this window open. It will check prices every 6 hours.
echo ------------------------------------------------

rem Command to run the worker script
python worker.py

rem Deactivate virtual environment when the worker stops
deactivate

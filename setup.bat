@echo off
rem --- SageMind Tech Services AI Shopping Assistant Setup Script (Windows) ---

echo ================================================
echo     SageMind Tech Services Setup Initializing...
echo ================================================

rem 1. Create Virtual Environment
if not exist venv (
    echo 1. Creating Python Virtual Environment (venv)...
    python -m venv venv
) else (
    echo 1. Virtual Environment 'venv' already exists.
)

rem 2. Activate Virtual Environment
echo 2. Activating Virtual Environment...
call venv\Scripts\activate

rem 3. Install Dependencies from requirements.txt
echo 3. Installing required Python packages...
pip install -r requirements.txt

rem 4. Create Necessary Directories
echo 4. Creating necessary application directories...
mkdir app\static\css 2>nul
mkdir app\static\images 2>nul
mkdir app\templates 2>nul

rem 5. Create a placeholder .env file
if not exist .env (
    echo 5. Creating placeholder .env file...
    echo # Environment variables for SageMind Tech Services > .env
    echo LOG_LEVEL=INFO >> .env
    echo AFFILIATE_ID=SM_TECH_001 >> .env
)

echo ================================================
echo E S T A B L I S H E D : Setup Complete!
echo ------------------------------------------------
echo Next Steps (Ensure you are in the project root):
echo -> Start the API server:   start_api.bat
echo -> Start the worker:       start_worker.bat
echo ================================================

pause

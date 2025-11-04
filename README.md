# 🛒 SageMind Tech Services: AI Shopping Assistant

This repository hosts the backend API and worker service for the **SageMind AI Shopping Assistant**. The system is built with **FastAPI** and uses **Python** for product tracking, price scraping, and AI-powered recommendations (Chatbot and Embeddings).

It is optimized for Windows environments using simple `.bat` scripts for easy setup and launch.

##  Features

* **Product Tracking:** Save product URLs for continuous price monitoring.
* **AI Chatbot:** GPT-2 model for answering shopping-related queries.
* **Price Alerts:** Email notifications when a product drops below a target price.
* **Asynchronous Worker:** Background process for scheduled web scraping.
* **Interactive Dashboard:** A simple frontend for tracking products and using the chatbot (`http://127.0.0.1:8000`).

##  Getting Started (Windows User Guide)

Follow these steps precisely to set up and run the entire application environment. **You must be in the project's root directory (`AI-Shopping-Assistant/`) for all commands.**

### Step 1: Automated Setup (One-Time)

This script creates the virtual environment (`venv`), installs all Python dependencies, and sets up the database (`shopping_assistant.db`).

1.  Open **PowerShell** or **Command Prompt** and navigate to the project root.
2.  Run the setup script:

    ```bash
    .\setup.bat
    ```
    *(Wait for this process to finish. It downloads several large AI models.)*

### Step 2: Start the Core Services (Two Separate Terminals)

The application requires two simultaneous processes. Open two separate terminal windows for this step.

#### Terminal 1: Start the API Server

This process runs the FastAPI web server.

1.  Navigate to the project root.
2.  Run the API script (use `.\` in PowerShell):

    ```bash
    .\start_api.bat
    ```
    **Result Check:** The terminal should show `Uvicorn running on http://127.0.0.1:8000`. Keep this window open.

#### Terminal 2: Start the Background Worker

This process handles scheduled scraping and price alert checks.

1.  Open a **second, separate terminal** and navigate to the project root.
2.  Run the worker script:

    ```bash
    .\start_worker.bat
    ```
    **Result Check:** The terminal should show `Worker sleeping for 21600 seconds...`. Keep this window open.

### Step 3: Access the Dashboard

Once both terminals are running, open your web browser and navigate to the main dashboard:

$$\text{http://127.0.0.1:8000}$$

You can now use the forms to:
1.  **Track New Product:** Input a URL, Name, and Store.
2.  **Set Price Alert:** Set a target price for any tracked product.
3.  **Use the Chatbot:** Ask the AI shopping assistant questions.

##  Project Structure

| File/Directory | Purpose |
| :--- | :--- |
| `app/main.py` | FastAPI application entry point, startup events, and route registration (Fixes the 404 error). |
| `app/templates/index.html` | The **interactive frontend dashboard** (SPA) for all user interactions. |
| `app/routes/` | Contains all API endpoint definitions (`products.py`, `chatbot.py`, etc.). |
| `worker.py` | The standalone script for running background scraping and alert checks. |
| **`setup.bat`** | **Automated setup for Windows.** |
| **`start_api.bat`** | **Starts the FastAPI server.** |
| **`start_worker.bat`** | **Starts the background worker.** |
| `requirements.txt` | Python dependency list (locked versions). |

##  Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Couldn't connect to server"** | The API server failed to start. | Ensure **Terminal 1** shows the `Uvicorn running...` message. If not, re-run `.\start_api.bat`. |
| **"Failed to add product: Server error" (404)** | The API routes are not being registered. | **CRITICAL:** Ensure `app/main.py` has the final, correct code (with `app.include_router(...)`) and restart the server. |
| **"Error: Could not connect to chatbot"** | AI models failed to load. | Re-run `.\setup.bat` to ensure all AI dependencies (`torch`, etc.) are installed correctly. |
| **`start_api.bat` not found** | Using PowerShell incorrectly. | Use the correct PowerShell command: `.\start_api.bat` (prefix with `.\`). |

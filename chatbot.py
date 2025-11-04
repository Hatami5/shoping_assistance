# AI-Shopping-Assistant/app/routes/chatbot.py

from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
from ..chatbot import generate_chat_response # Import the core AI logic
from ..utils.logger import setup_logging

router = APIRouter()
logger = setup_logging(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Handles incoming chat requests, passes them to the local AI model, 
    and returns the assistant's response.
    """
    logger.info(f"Received chat request from session: {request.session_id}")
    
    # 1. Input Validation (handled automatically by FastAPI/Pydantic)

    try:
        # 2. Call the core AI generation function
        # NOTE: This uses the blocking model inference, which FastAPI 
        # automatically runs in an external thread pool (run_in_threadpool).
        assistant_text = generate_chat_response(request.user_message)
        
        # 3. Construct the response object
        response = ChatResponse(
            assistant_response=assistant_text,
            session_id=request.session_id
        )
        
        return response

    except Exception as e:
        logger.error(f"Chatbot processing error: {e}")
        # Return a 500 Internal Server Error in case of model failure
        raise HTTPException(
            status_code=500, 
            detail="The AI assistant is currently unable to process your request."
        )

# --- Update app/main.py to include this new router ---

# In app/main.py, ensure you change this line:
# from .routes import products, recommender, scraper 
# TO THIS:
# from .routes import products, recommender, scraper, chatbot 

# And include the router:
# app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["AI Chatbot"])
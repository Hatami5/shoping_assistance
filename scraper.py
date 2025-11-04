# AI-Shopping-Assistant/app/routes/scraper.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio # Used for async operations simulation
from ..utils.logger import setup_logging
from ..services.proxy_service import proxy_service # Import our proxy manager
from ..database.db import get_db, SessionLocal
from ..database.db import Product
from sqlalchemy.orm import Session

router = APIRouter()
logger = setup_logging(__name__)

# --- Request Schema for Scraper ---

class ScrapingRequest(BaseModel):
    """Schema for requesting a product scrape."""
    url: HttpUrl
    product_name: str
    store: str
    
class ScrapingResponse(BaseModel):
    """Schema for the scraping response."""
    status: str
    message: str
    product_id: Optional[int] = None
    
# --- Placeholder Scraping Function (I/O BOUND TASK) ---

# In a real app, this function would live in a service file (e.g., app/services/scraper.py)
# and use libraries like httpx and beautifulsoup4.

async def perform_scraping_task(db: Session, request: ScrapingRequest, proxy_dict: Optional[dict]):
    """
    Simulates the actual web scraping process. Since this is a blocking
    I/O operation, FastAPI will automatically run it in a thread pool.
    """
    url = str(request.url)
    logger.info(f"Starting scrape for {url} using proxy: {proxy_dict is not None}")
    
    # 1. Simulate the work (fetching and parsing)
    await asyncio.sleep(2) # Simulate network latency and processing time

    # 2. Simulate Success and Data Extraction
    # In a real scenario, this price would be parsed from the HTML
    simulated_price = 150.0 + (hash(url) % 500) / 100.0 # Creates a "random" price
    
    # 3. Save to Database
    # Check if product exists (simplified logic)
    product = db.query(Product).filter(Product.url == url).first()

    if product:
        # Update existing product
        product.current_price = simulated_price
        product.last_scraped = datetime.utcnow()
        db.commit()
        db.refresh(product)
        logger.info(f"Updated price for Product ID {product.id} to ${simulated_price:.2f}")
    else:
        # Create new product
        new_product = Product(
            name=request.product_name,
            url=url,
            store=request.store,
            current_price=simulated_price
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        product = new_product
        logger.info(f"New product scraped and created: ID {product.id}")

    return product.id

# --- FastAPI Endpoint ---

@router.post("/trigger", response_model=ScrapingResponse)
async def trigger_scrape(
    request: ScrapingRequest, 
    db: Session = Depends(get_db)
):
    """
    Triggers a scraping task for a specific product URL.
    """
    # 1. Get Proxy
    proxy_dict = proxy_service.get_random_proxy()
    
    try:
        # 2. Execute the Scraping Task
        # FastAPI handles running blocking synchronous code (like the HTTP request/parsing) 
        # inside the thread pool, but our simulation uses 'await asyncio.sleep' 
        # so we keep it async.
        product_id = await perform_scraping_task(db, request, proxy_dict)
        
        return ScrapingResponse(
            status="success",
            message=f"Scraping completed and price updated/created for product ID {product_id}.",
            product_id=product_id
        )
        
    except Exception as e:
        # 3. Handle Errors
        logger.error(f"Scraping failed for {request.url}: {e}")
        # Report the proxy failure if used
        if proxy_dict:
            proxy_service.report_failure(proxy_dict.get('http://'))
            
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: Could not fetch data from {request.store}. Error: {str(e)}"
        )
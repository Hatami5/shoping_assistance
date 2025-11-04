# AI-Shopping-Assistant/worker.py

import time
import asyncio
# Import UTC explicitly from datetime
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any

# --- ABSOLUTE IMPORTS ---
from app.database.db import SessionLocal, Product, PriceAlert, create_db_and_tables
from app.utils.logger import setup_logging
from app.services.email_alerts import email_service
from app.services.affiliate import affiliate_service
# Import the async scraping function directly from the routes module
from app.routes.scraper import perform_scraping_task as scrape_product 
# ------------------------

logger = setup_logging(__name__)

# --- Configuration for Worker Scheduling (in seconds) ---
# Check every 6 hours (6 hours * 60 minutes * 60 seconds)
PRODUCT_CHECK_INTERVAL = 3600 * 6 

def get_products_to_scrape() -> List[Product]:
    """
    Queries the database for products that are due for a price check.
    Uses UTC to handle time comparison correctly.
    """
    db = SessionLocal()
    try:
        # Check products scraped before the threshold (6 hours ago)
        # Using datetime.now(UTC) for time-zone aware comparison
        threshold_time = datetime.now(UTC) - timedelta(seconds=PRODUCT_CHECK_INTERVAL)
        
        # Get products that have never been scraped OR were last scraped before the threshold
        products_due = db.query(Product).filter(
            (Product.last_scraped == None) | (Product.last_scraped < threshold_time)
        ).all()
        
        logger.info(f"Found {len(products_due)} products due for scraping.")
        return products_due
    except Exception as e:
        logger.error(f"Error fetching products due for scrape: {e}")
        return []
    finally:
        db.close()

def check_and_send_price_alerts(product_data: Dict[str, Any]):
    """
    Checks all active price alerts for a given product and sends emails if the price 
    has dropped below the target.
    """
    db = SessionLocal()
    product_id = product_data['id']
    
    try:
        current_price = product_data['current_price']
        
        # Find active alerts for this product
        active_alerts = db.query(PriceAlert).filter(
            PriceAlert.product_id == product_id,
            PriceAlert.active == True,
            PriceAlert.target_price > current_price # Price drop condition
        ).all()
        
        if not active_alerts:
            return

        product_url = product_data['url']
        
        for alert in active_alerts:
            # 1. Create a monetized link for the email notification
            affiliate_link = affiliate_service.convert_to_affiliate_link(product_url)
            
            # 2. Prepare data for the email service
            alert_data = {
                "product_name": product_data.get('name', 'Product'),
                "target_price": alert.target_price,
                "current_price": current_price,
                "product_url": affiliate_link,
                "store": product_data.get('store', 'Store')
            }
            
            # 3. Send the email notification
            success = email_service.send_price_alert(alert.user_email, alert_data)
            
            # 4. Deactivate the alert to prevent spam (typical approach after a successful alert)
            if success:
                alert.active = False
                db.commit()
                logger.info(f"Price alert sent and deactivated for alert ID {alert.id}.")

    except Exception as e:
        logger.error(f"Error during price alert processing for product ID {product_id}: {e}")
    finally:
        db.close()

async def run_scrape_cycle():
    """
    Main function to run the scraping and price alert check cycle.
    """
    logger.info("--- WORKER: Starting scrape cycle ---")
    products_to_scrape = get_products_to_scrape()
    
    for product in products_to_scrape:
        logger.info(f"Processing scrape for Product ID: {product.id} ({product.name})...")
        
        # 1. Prepare a mock request object for the scraper function (needed for type compatibility)
        mock_request = type('MockRequest', (object,), {
            'url': product.url, 
            'product_name': product.name,
            'store': product.store
        })()
        
        db = SessionLocal()
        try:
            # 2. Run the asynchronous scraping task 
            updated_product = await scrape_product(db, mock_request, product.id) 
            
            # 3. Check for alerts immediately after a successful price update
            if updated_product:
                # __dict__ converts the ORM object to a dictionary for easier passing
                check_and_send_price_alerts(updated_product.__dict__)
                
        except Exception as e:
            # Log the error but don't stop the worker
            logger.error(f"Failed to execute scraping or alert check for Product ID {product.id}: {e}")
        finally:
            db.close()
            
    logger.info("--- WORKER: Scrape cycle finished ---")

async def start_worker():
    """
    Starts the continuous worker loop.
    """
    logger.info(f"Worker process starting. Checking products every {PRODUCT_CHECK_INTERVAL/3600} hours.")
    
    # Run database setup before starting the infinite loop
    create_db_and_tables()
    
    while True:
        await run_scrape_cycle()
        logger.info(f"Worker sleeping for {PRODUCT_CHECK_INTERVAL} seconds...")
        await asyncio.sleep(PRODUCT_CHECK_INTERVAL)

if __name__ == "__main__":
    # If run standalone, use asyncio to start the async loop
    asyncio.run(start_worker())

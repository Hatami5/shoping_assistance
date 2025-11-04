# AI-Shopping-Assistant/app/routes/products.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import dependencies
from ..database.db import get_db, Product, PriceAlert
from ..schemas import (
    ProductCreate, 
    Product as ProductSchema, 
    PriceAlertCreate, 
    PriceAlert as PriceAlertSchema
)
from ..utils.logger import setup_logging

router = APIRouter()
logger = setup_logging(__name__)

# --- 1. Product Listing and Creation ---

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product entry in the database. 
    This is typically used after a successful scrape.
    """
    # Check if a product with this URL already exists to prevent duplication
    db_product = db.query(Product).filter(Product.url == product.url).first()
    if db_product:
        logger.warning(f"Product already exists: {product.url}")
        # Return the existing product
        return db_product 

    # Create new product entry
    db_product = Product(
        name=product.name,
        url=product.url,
        store=product.store,
        current_price=product.current_price,
        description=product.description
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Created new product entry: ID {db_product.id}")
    return db_product

@router.get("/", response_model=List[ProductSchema])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all products in the database.
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(products)} products from the database.")
    return products

# --- 2. Price Alert Management ---

@router.post("/alerts", response_model=PriceAlertSchema, status_code=status.HTTP_201_CREATED)
def create_price_alert(alert: PriceAlertCreate, db: Session = Depends(get_db)):
    """
    Sets a new price alert for a product for a specific user email.
    """
    # 1. Verify the product exists
    product = db.query(Product).filter(Product.id == alert.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Product with ID {alert.product_id} not found."
        )

    # 2. Check if the target price is reasonable (e.g., lower than current price)
    if alert.target_price >= product.current_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target price (${alert.target_price:.2f}) must be lower than current price (${product.current_price:.2f})."
        )

    # 3. Create the alert
    db_alert = PriceAlert(
        product_id=alert.product_id,
        user_email=alert.user_email,
        target_price=alert.target_price,
        active=True
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    logger.info(f"New price alert set for Product ID {alert.product_id} at target price ${alert.target_price:.2f}.")
    return db_alert

@router.get("/alerts/{email}", response_model=List[PriceAlertSchema])
def read_price_alerts_by_email(email: str, db: Session = Depends(get_db)):
    """
    Retrieves all active price alerts for a given user email.
    """
    alerts = db.query(PriceAlert).filter(PriceAlert.user_email == email, PriceAlert.active == True).all()
    return alerts
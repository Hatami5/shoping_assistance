# AI-Shopping-Assistant/app/routes/recommender.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Import dependencies
from ..database.db import get_db
from ..ai.recommender import find_similar_products 
from ..utils.logger import setup_logging

router = APIRouter()
logger = setup_logging(__name__)

# --- Response Schema (Pydantic is used for validation, but we return a custom dict) ---

# We don't define a formal Pydantic schema here as the output is complex, 
# but in a production app, you would define a schema like:
# class Recommendation(BaseModel):
#     product_id: int
#     name: str
#     similarity_score: float
#     current_price: float
# ...

@router.get("/similar/{product_id}", response_model=List[Dict[str, Any]])
def get_similar_products(
    product_id: int, 
    limit: int = 5, 
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of products semantically similar to the product_id provided.

    The recommendations are based on Cosine Similarity of the product embeddings.
    """
    logger.info(f"Requesting top {limit} similar products for Product ID: {product_id}")
    
    if limit > 20:
        limit = 20 # Cap the limit to prevent excessive load

    try:
        # Call the core recommendation logic
        recommendations = find_similar_products(db, product_id, limit)

        if not recommendations:
            logger.warning(f"No recommendations found for Product ID {product_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID {product_id} not found or has no similar items."
            )

        return recommendations

    except HTTPException as e:
        # Re-raise explicit HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error processing recommendation for ID {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while running the recommendation engine."
        )


@router.post("/refresh-embedding/{product_id}")
def refresh_product_embedding_endpoint(product_id: int, db: Session = Depends(get_db)):
    """
    Manually triggers the re-generation and saving of a single product's embedding.
    (Useful after an update to the product description.)
    """
    from ..ai.recommender import update_product_embedding # Import for local use
    
    try:
        update_product_embedding(db, product_id)
        return {"status": "success", "message": f"Embedding for Product ID {product_id} updated."}
    except Exception as e:
        logger.error(f"Failed to refresh embedding for Product ID {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh embedding. Check server logs."
        )
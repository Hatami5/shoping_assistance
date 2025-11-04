# AI-Shopping-Assistant/app/services/affiliate.py

from typing import Dict
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from ..utils.logger import setup_logging

logger = setup_logging(__name__)

# --- Configuration (Simulated Affiliate IDs for various stores) ---
# In reality, this lookup would be more complex and managed by an external provider API.
AFFILIATE_CONFIG = {
    "amazon.com": {"id": "ai-shop-20", "param": "tag"},
    "ebay.com": {"id": "ai-shop-assistant-20", "param": "_sasl"},
    "bestbuy.com": {"id": "bb-ai-shop", "param": "siteID"},
}
DEFAULT_AFFILIATE_ID = "ai-general-20"


class AffiliateService:
    """
    Converts standard e-commerce URLs into tracked affiliate links 
    for revenue generation.
    """
    
    def __init__(self):
        logger.info("AffiliateService initialized.")
        
    def get_domain(self, url: str) -> str:
        """Extracts the base domain name from a URL."""
        try:
            # Netloc is the domain (e.g., www.amazon.com)
            netloc = urlparse(url).netloc
            # Simple cleanup to get the base domain (e.g., amazon.com)
            if netloc.startswith('www.'):
                return netloc[4:]
            return netloc
        except:
            return ""

    def convert_to_affiliate_link(self, product_url: str) -> str:
        """
        Takes a product URL and injects the corresponding affiliate tracking parameters.
        """
        domain = self.get_domain(product_url)
        config = AFFILIATE_CONFIG.get(domain)
        
        if not config:
            logger.debug(f"No direct affiliate config found for domain: {domain}. Returning original URL.")
            return product_url

        try:
            # 1. Parse the URL into components
            parsed_url = urlparse(product_url)
            query_params = parse_qs(parsed_url.query)
            
            # 2. Inject or replace the affiliate tracking parameter
            affiliate_param = config["param"]
            affiliate_id = config["id"]
            
            query_params[affiliate_param] = [affiliate_id] # Replace existing or add new
            
            # 3. Rebuild the query string
            new_query = urlencode(query_params, doseq=True)
            
            # 4. Rebuild the final URL
            affiliate_link = urlunparse(parsed_url._replace(query=new_query))
            
            logger.debug(f"Converted {domain} link to affiliate link.")
            return affiliate_link
            
        except Exception as e:
            logger.error(f"Error converting URL {product_url} to affiliate link: {e}")
            return product_url # Return original URL on failure

affiliate_service = AffiliateService()

# --- Example Usage (for testing the module directly) ---
if __name__ == "__main__":
    test_amazon_url = "https://www.amazon.com/product/xyz?ref=oldtag&other=data"
    test_ebay_url = "https://ebay.com/itm/123456"
    test_generic_url = "https://my-local-store.com/item/a"
    
    print(f"Amazon Affiliate: {affiliate_service.convert_to_affiliate_link(test_amazon_url)}")
    print(f"eBay Affiliate:   {affiliate_service.convert_to_affiliate_link(test_ebay_url)}")
    print(f"Generic Result:   {affiliate_service.convert_to_affiliate_link(test_generic_url)}")
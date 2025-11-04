# AI-Shopping-Assistant/app/services/proxy_service.py

from typing import List, Optional
from random import choice
from ..utils.logger import setup_logging

logger = setup_logging(__name__)

class ProxyService:
    """
    Manages a list of proxy servers for web scraping. 
    In a production application, this would handle health checks, rotation logic,
    and credentials for commercial proxy services.
    """
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initializes the service with a list of proxies.
        Proxies should be in the format: 'http://user:pass@host:port'
        """
        # Placeholder list of proxies. Replace with real proxies in production.
        self.proxies: List[str] = proxy_list if proxy_list else [
            # Example Proxy List (for illustration only)
            "http://scraper_user1:pass1@203.0.113.1:8080",
            "http://scraper_user2:pass2@198.51.100.2:8080",
            None # Allow direct connection (no proxy) as an option
        ]
        
        logger.info(f"ProxyService initialized with {len(self.proxies)} endpoints.")

    def get_random_proxy(self) -> Optional[dict]:
        """
        Selects a random proxy from the list.
        Returns a dictionary formatted for use with libraries like 'httpx' or 'requests'.
        """
        proxy_url = choice(self.proxies)
        
        if proxy_url is None:
            logger.debug("Using direct connection (No proxy selected).")
            return None
        
        # Format for standard Python HTTP clients
        proxy_dict = {
            "http://": proxy_url,
            "https://": proxy_url,
        }
        logger.debug(f"Selected proxy: {proxy_url.split('@')[-1]}")
        return proxy_dict

    def report_failure(self, failed_proxy: str):
        """
        Logs a failed proxy. In production, this would temporarily remove the proxy 
        from the active list for a cool-down period.
        """
        if failed_proxy:
            logger.warning(f"Proxy failed: {failed_proxy.split('@')[-1]}. Should be temporarily removed.")
        
# Initialize the service globally (or as a FastAPI dependency)
proxy_service = ProxyService()

# --- Example Usage (for testing the module directly) ---
if __name__ == "__main__":
    test_proxy = proxy_service.get_random_proxy()
    print(f"Random Proxy Selected: {test_proxy}")
    if test_proxy:
        proxy_service.report_failure(test_proxy['http://'])
"""Browser management functionality for YouTube Community Scraper"""
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

def create_driver(proxy_manager=None):
    """Create a new driver with the next proxy."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.set_preference('network.http.connection-timeout', 30)
    
    # Only set up proxy if proxy_manager is provided
    seleniumwire_options = {}
    if proxy_manager:
        proxy_info = proxy_manager.get_next_proxy()
        seleniumwire_options = proxy_manager.get_seleniumwire_options(proxy_info)
        print(f"Using proxy: {proxy_info['host']}:{proxy_info['port']}")
    
    driver = webdriver.Firefox(
        options=firefox_options,
        seleniumwire_options=seleniumwire_options
    )
    return driver

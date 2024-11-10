"""Browser management functionality for YouTube Community Scraper"""
import logging
from playwright.sync_api import sync_playwright

def create_driver(proxy_manager=None, browser_type='chromium'):
    """Create a new browser instance with the next proxy.
    
    Args:
        proxy_manager: Optional ProxyManager instance for proxy support
        browser_type: Browser to use ('chromium', 'firefox', or 'webkit')
    """
    logger = logging.getLogger('post_archiver')
    logger.info(f"Initializing {browser_type} browser")
    
    playwright = sync_playwright().start()
    logger.debug("Playwright started")
    
    # Select browser based on type
    browser_types = {
        'chromium': playwright.chromium,
        'firefox': playwright.firefox,
        'webkit': playwright.webkit
    }
    
    browser_launcher = browser_types.get(browser_type.lower(), playwright.chromium)
    logger.debug(f"Selected browser launcher: {browser_type}")
    
    # Install browser if not already installed
    try:
        logger.debug("Checking if browser is installed")
        browser_launcher.launch(headless=True).close()
        logger.debug("Browser is already installed")
    except Exception as e:
        if "Executable doesn't exist" in str(e):
            logger.info(f"Installing {browser_type} browser...")
            import subprocess
            import sys
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", browser_type],
                capture_output=True,
                text=True
            )
            logger.debug(f"Installation output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Installation warnings: {result.stderr}")
        else:
            logger.error(f"Failed to launch browser: {str(e)}")
            raise e
    
    # Configure browser options
    browser_args = ['--headless']
    logger.debug(f"Browser arguments: {browser_args}")
    
    # Configure proxy if provided
    proxy_config = None
    if proxy_manager:
        proxy_info = proxy_manager.get_next_proxy()
        proxy_config = proxy_manager.get_proxy_config(proxy_info)
        logger.info(f"Using proxy: {proxy_info['host']}:{proxy_info['port']}")
        logger.debug(f"Full proxy configuration: {proxy_config}")
    else:
        logger.debug("No proxy configuration provided")

    try:
        # Launch browser
        logger.debug("Launching browser with configuration")
        browser = browser_launcher.launch(
            args=browser_args,
            proxy=proxy_config
        )
        logger.debug("Browser launched successfully")
        
        # Create context and page
        logger.debug("Creating browser context")
        context = browser.new_context()
        logger.debug("Creating new page")
        page = context.new_page()
        
        # Enable detailed browser logging if trace is enabled
        if logger.getEffectiveLevel() <= logging.DEBUG:
            page.on("console", lambda msg: logger.debug(f"Browser console {msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: logger.error(f"Page error: {exc}"))
            def on_request_failed(request):
                try:
                    error_text = request.failure
                    if isinstance(error_text, dict):
                        error_text = error_text.get('errorText', 'Unknown error')
                    elif callable(getattr(request, 'failure', None)):
                        error_text = request.failure().get('errorText', 'Unknown error')
                    else:
                        error_text = str(error_text)
                    logger.warning(f"Request failed: {request.url} - {error_text}")
                except Exception as e:
                    logger.debug(f"Error handling request failure: {str(e)}")
            page.on("requestfailed", on_request_failed)
            logger.debug("Detailed browser logging enabled")
        
        # Add helper methods to make transition easier
        def quit_browser():
            logger.debug("Closing browser context and stopping playwright")
            context.close()
            browser.close()
            playwright.stop()
        
        def execute_script(script, *args):
            logger.debug(f"Executing script: {script[:100]}{'...' if len(script) > 100 else ''}")
            return page.evaluate(script, *args)
        
        page.quit = quit_browser
        page.execute_script = execute_script
        
        # Store browser type for retries
        page.browser_type = browser_type
        
        logger.info(f"{browser_type.capitalize()} browser initialized successfully")
        return page
        
    except Exception as e:
        logger.error(f"Error with {browser_type}: {str(e)}")
        if browser_type != 'chromium':
            logger.warning(f"Falling back to Chromium browser")
            try:
                playwright.stop()
            except:
                pass
            return create_driver(proxy_manager, browser_type='chromium')
        else:
            raise e

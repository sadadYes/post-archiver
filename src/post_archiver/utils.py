"""Utility functions for YouTube Community Scraper"""
import os
import logging
from pathlib import Path
from datetime import datetime
import requests
import browser_cookie3

def setup_logging(verbose, trace):
    """Configure logging based on verbosity level."""
    if trace:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    elif verbose:
        log_level = logging.INFO
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
    else:
        log_level = logging.WARNING
        log_format = '%(levelname)s - %(message)s'
    
    # Create logger for our package
    logger = logging.getLogger('post_archiver')
    logger.setLevel(log_level)
    
    # Remove any existing handlers from both root and package loggers
    logging.root.handlers = []
    logger.handlers = []
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    
    # Add handler to both root and package loggers
    logging.root.addHandler(console_handler)
    logger.addHandler(console_handler)
    
    # Prevent double logging
    logger.propagate = False
    
    if trace:
        logger.debug("Debug logging enabled")
    elif verbose:
        logger.info("Verbose logging enabled")

def create_directories(channel_name, timestamp, base_dir=None, create_images_dir=False):
    """Create output directories for saving data."""
    logger = logging.getLogger('post_archiver')
    try:
        if base_dir:
            base_dir = Path(base_dir)
            logger.debug(f"Using specified base directory: {base_dir}")
        else:
            base_dir = Path.cwd()
            logger.debug(f"Using current directory as base: {base_dir}")
        
        # Create channel directory
        channel_dir = base_dir / f"{channel_name}_{timestamp}"
        channel_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Created channel directory: {channel_dir}")
        
        # Create images directory if requested
        images_dir = None
        if create_images_dir:
            images_dir = channel_dir / 'images'
            images_dir.mkdir(exist_ok=True)
            logger.info(f"Created images directory: {images_dir}")
        
        return channel_dir, images_dir
    except Exception as e:
        logger.error(f"Failed to create directories: {str(e)}")
        # Fallback to current directory
        fallback_dir = Path.cwd()
        logger.warning(f"Falling back to current directory: {fallback_dir}")
        return fallback_dir, None if not create_images_dir else fallback_dir / 'images'

def download_image(url, save_path):
    """Download image from URL and save to specified path."""
    logger = logging.getLogger('post_archiver')
    try:
        logger.debug(f"Downloading image from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Successfully downloaded image to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading image {url}: {str(e)}")
        return False

def get_browser_cookies(browser_name='chrome', domain='.youtube.com'):
    """Get cookies from browser for specified domain.
    
    Args:
        browser_name: Browser to get cookies from ('chrome', 'firefox', 'edge', 'opera')
        domain: Domain to filter cookies for (default: .youtube.com)
    """
    logger = logging.getLogger('post_archiver')
    
    browser_functions = {
        'chrome': browser_cookie3.chrome,
        'firefox': browser_cookie3.firefox,
        'edge': browser_cookie3.edge,
        'opera': browser_cookie3.opera,
    }
    
    try:
        cookie_fn = browser_functions.get(browser_name.lower())
        if not cookie_fn:
            raise ValueError(f"Unsupported browser: {browser_name}")
            
        logger.info(f"Getting cookies from {browser_name}")
        cookies = cookie_fn(domain_name=domain)
        
        # Convert to Playwright format
        playwright_cookies = []
        for cookie in cookies:
            # Ensure secure is boolean
            secure = bool(cookie.secure) if isinstance(cookie.secure, (int, bool)) else False
            
            # Convert cookie to Playwright format
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': secure,
                'httpOnly': bool(cookie.has_nonstandard_attr('HttpOnly')),
                'sameSite': 'Lax',  # Default value
            }
            
            # Only add expires if it's a valid number
            if hasattr(cookie, 'expires') and cookie.expires:
                try:
                    expires = int(cookie.expires)
                    if expires > 0:
                        cookie_dict['expires'] = expires
                except (ValueError, TypeError):
                    pass  # Skip expires if invalid
            
            playwright_cookies.append(cookie_dict)
        
        logger.info(f"Found {len(playwright_cookies)} cookies for {domain}")
        return playwright_cookies
        
    except Exception as e:
        logger.error(f"Failed to get cookies from {browser_name}: {str(e)}")
        return None

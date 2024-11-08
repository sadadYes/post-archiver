"""Utility functions for YouTube Community Scraper"""
import os
import logging
from pathlib import Path
from datetime import datetime
import requests

def setup_logging(verbose, trace):
    """Configure logging based on verbosity level."""
    if trace:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_directories(channel_name, timestamp, base_dir=None, create_images_dir=False):
    """Create output directories for saving data."""
    try:
        if base_dir:
            base_dir = Path(base_dir)
        else:
            base_dir = Path.cwd()
        
        # Create channel directory
        channel_dir = base_dir / f"{channel_name}_{timestamp}"
        channel_dir.mkdir(exist_ok=True, parents=True)
        
        # Create images directory if requested
        images_dir = None
        if create_images_dir:
            images_dir = channel_dir / 'images'
            images_dir.mkdir(exist_ok=True)
        
        return channel_dir, images_dir
    except Exception as e:
        logging.error(f"Failed to create directories: {str(e)}")
        # Fallback to current directory
        return Path.cwd(), None if not create_images_dir else Path.cwd() / 'images'

def download_image(url, save_path):
    """Download image from URL and save to specified path."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logging.error(f"Error downloading image {url}: {str(e)}")
        return False

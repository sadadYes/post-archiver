"""YouTube Community Posts Scraper"""
from .scraper import get_all_posts
from .proxy import ProxyManager
from .browser import create_driver

__version__ = "1.2.1"

__all__ = ["get_all_posts", "ProxyManager", "create_driver"]

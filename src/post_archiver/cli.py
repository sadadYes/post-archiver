"""Command-line interface for YouTube Community Scraper"""
import argparse
import logging
from pathlib import Path
from urllib.parse import urlparse

from .proxy import ProxyManager
from .browser import create_driver
from .scraper import get_all_posts
from .utils import setup_logging

VERSION = "1.1.0"

def validate_url(url):
    """Validate YouTube community URL."""
    parsed = urlparse(url)
    if not parsed.netloc == 'www.youtube.com' or not '/community' in parsed.path:
        raise argparse.ArgumentTypeError(f"Invalid YouTube community URL: {url}")
    return url

def validate_proxy(value):
    """Validate proxy string or file."""
    if Path(value).is_file():
        # Validate file content
        with open(value) as f:
            proxies = [line.strip() for line in f if line.strip()]
            for proxy in proxies:
                # Check each proxy in file has valid format
                if not any(proxy.startswith(scheme + '://') for scheme in ['http', 'https']):
                    raise argparse.ArgumentTypeError(
                        f"Invalid proxy format in {value}: {proxy}\n"
                        f"Format should be: <scheme>://<username>:<password>@<host>:<port>\n"
                        f"Supported schemes: http, https"
                    )
        return value
    else:
        # Validate single proxy string
        if not any(value.startswith(scheme + '://') for scheme in ['http', 'https']):
            raise argparse.ArgumentTypeError(
                f"Invalid proxy format: {value}\n"
                f"Format should be: <scheme>://<username>:<password>@<host>:<port>\n"
                f"Supported schemes: http, https"
            )
        return value

def validate_image_quality(value):
    """Validate image quality option."""
    if value.lower() not in ['sd', 'hd', 'all']:
        raise argparse.ArgumentTypeError("Image quality must be 'sd', 'hd', or 'all'")
    return value.lower()

def validate_amount(value):
    """Validate amount of posts to get."""
    try:
        amount = int(value)
        if amount <= 0:
            return float('inf')  # Return infinity for max posts
        return amount
    except ValueError:
        if value.lower() == 'max':
            return float('inf')
        raise argparse.ArgumentTypeError("Amount must be a positive integer or 'max'")

def parse_args():
    parser = argparse.ArgumentParser(
        description="YouTube Community Posts Scraper",
        usage='%(prog)s [OPTIONS] url [amount]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Proxy format:
  Single proxy: <scheme>://<username>:<password>@<host>:<port>
  Proxy file: One proxy per line using the same format
  Supported schemes: http, https
  Note: SOCKS5 proxies are supported but without authentication

Amount:
  Specify number of posts to scrape (default: max)
  Use 'max' or any number <= 0 to scrape all posts

Examples:
  %(prog)s https://www.youtube.com/@channel/community
  %(prog)s https://www.youtube.com/@channel/community 50
  %(prog)s -c -i -d -q hd https://www.youtube.com/@channel/community max
  %(prog)s --proxy proxies.txt https://www.youtube.com/@channel/community 100
  %(prog)s --proxy http://username:password@host:port https://www.youtube.com/@channel/community
  %(prog)s --proxy https://username:password@host:port https://www.youtube.com/@channel/community
  %(prog)s --proxy socks5://host:port https://www.youtube.com/@channel/community
        """
    )
    
    parser.add_argument('url', type=validate_url, 
                       help="YouTube channel community URL")
    
    parser.add_argument('amount', type=validate_amount, nargs='?', 
                       default=float('inf'),
                       help="Amount of posts to get (default: max)")
    
    parser.add_argument('-c', '--get-comments', action='store_true',
                      help="Get comments from posts (WARNING: This is slow) (default: False)")
    
    parser.add_argument('-i', '--get-images', action='store_true',
                      help="Get images from posts (default: False)")
    
    parser.add_argument('-d', '--download-images', action='store_true',
                      help="Download images (requires --get-images)")
    
    parser.add_argument('-q', '--image-quality', type=validate_image_quality,
                      default='all', help="Image quality: sd, hd, or all (default: all)")
    
    parser.add_argument('--proxy', type=validate_proxy,
                      help="Proxy file or single proxy string")
    
    parser.add_argument('-o', '--output', type=Path,
                      help="Output directory (default: current directory)")
    
    parser.add_argument('-v', '--verbose', action='store_true',
                      help="Show basic progress information")
    
    parser.add_argument('-t', '--trace', action='store_true',
                      help="Show detailed debug information")
    
    parser.add_argument('--version', action='version',
                      version=f'%(prog)s {VERSION}')
    
    # Add browser selection argument
    parser.add_argument('--browser', type=str, choices=['chromium', 'firefox', 'webkit'],
                      default='chromium', help="Browser to use (default: chromium)")
    
    args = parser.parse_args()
    
    # Validate dependent arguments
    if args.download_images and not args.get_images:
        parser.error("--download-images requires --get-images")
    
    if args.image_quality != 'all' and not args.get_images:
        parser.error("--image-quality requires --get-images")
    
    return args

def main():
    args = parse_args()
    setup_logging(args.verbose, args.trace)
    
    # Configure output directory
    output_dir = args.output if args.output else Path.cwd()
    
    # Configure proxy
    if args.proxy:
        if Path(args.proxy).is_file():
            proxy_manager = ProxyManager(proxy_file=args.proxy)
        else:
            proxy_manager = ProxyManager(single_proxy=args.proxy)
    else:
        proxy_manager = None
    
    # Create initial driver with selected browser
    driver = create_driver(proxy_manager, browser_type=args.browser)
    
    try:
        driver.goto(args.url)
        driver.wait_for_selector("yt-formatted-string#content-text")
        
        get_all_posts(
            driver=driver,
            proxy_manager=proxy_manager,
            get_comments=args.get_comments,
            get_images=args.get_images,
            download_images=args.download_images,
            image_quality=args.image_quality,
            output_dir=output_dir,
            verbose=args.verbose,
            trace=args.trace,
            max_posts=args.amount
        )
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()

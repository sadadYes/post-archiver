# YouTube Community Scraper

A Python tool to scrape posts from YouTube community tabs.

## Features

- Scrape posts from YouTube community tabs
- Download images from posts
- Collect post comments
- Multi-browser support (Chromium, Firefox, WebKit)
- Automatic browser installation
- Proxy support (HTTP/HTTPS with auth, SOCKS5 without auth)
- Progress saving
- Configurable output directory

## Installation

Install using pip:
```bash
pip install post-archiver
```

Or install from source:
```bash
git clone https://github.com/sadadYes/post-archiver.git
cd post-archiver
pip install -e .
```

## Requirements

- Python 3.7 or higher
- No manual browser installation needed - browsers are installed automatically when needed

## Usage

```
usage: post-archiver [OPTIONS] url [amount]

YouTube Community Posts Scraper

positional arguments:
  url                   YouTube channel community URL
  amount                Amount of posts to get (default: max)

options:
  -h, --help            show this help message and exit
  -c, --get-comments    Get comments from posts (WARNING: This is slow) (default: False)
  -i, --get-images      Get images from posts (default: False)
  -d, --download-images
                        Download images (requires --get-images)
  -q IMAGE_QUALITY, --image-quality IMAGE_QUALITY
                        Image quality: sd, hd, or all (default: all)
  --proxy PROXY         Proxy file or single proxy string
  -o OUTPUT, --output OUTPUT
                        Output directory (default: current directory)
  -v, --verbose         Show basic progress information
  -t, --trace          Show detailed debug information
  --browser {chromium,firefox,webkit}
                        Browser to use (default: chromium)
  --version            show program's version number and exit

Proxy format:
  Single proxy: <scheme>://<username>:<password>@<host>:<port>
  Proxy file: One proxy per line using the same format
  Supported schemes: http, https
  Note: SOCKS5 proxies are supported but without authentication

Amount:
  Specify number of posts to scrape (default: max)
  Use 'max' or any number <= 0 to scrape all posts

Examples:
  post-archiver https://www.youtube.com/@channel/community
  post-archiver https://www.youtube.com/@channel/community 50
  post-archiver -c -i -d -q hd https://www.youtube.com/@channel/community max
  post-archiver --browser firefox https://www.youtube.com/@channel/community
  post-archiver --proxy proxies.txt https://www.youtube.com/@channel/community 100
  post-archiver --proxy http://username:password@host:port https://www.youtube.com/@channel/community
  post-archiver --proxy https://username:password@host:port https://www.youtube.com/@channel/community
  post-archiver --proxy socks5://host:port https://www.youtube.com/@channel/community
```

## Browser Support

The scraper supports three browser engines:
- Chromium (default)
- Firefox
- WebKit

The appropriate browser will be automatically installed when first used. You can specify which browser to use with the `--browser` option.

## Proxy Support

The scraper supports the following proxy types:
- HTTP proxies with authentication
- HTTPS proxies with authentication
- SOCKS5 proxies (without authentication)

**Note:** SOCKS5 proxies with authentication are not supported due to limitations in the underlying browser automation.

## Logging

Two levels of logging are available:
- `--verbose (-v)`: Shows basic progress information
- `--trace (-t)`: Shows detailed debug information including browser console messages

## License

MIT License


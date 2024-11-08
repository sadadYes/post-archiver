# YouTube Community Post Scraper

A Python tool to scrape posts from YouTube community tabs.

## Dependencies

* Firefox browser needs to be installed
* GeckoDriver needs to be installed and in your PATH
* Python 3.7 or higher

## Features

- Scrape posts from YouTube community tabs
- Download images from posts
- Collect post comments
- Proxy support
- Progress saving
- Configurable output directory

## Installation

Download and install using pip:
```bash
pip install post-archiver
```

Alternatively, if you want to install from source:
```bash
git clone https://github.com/sadadYes/post-archiver.git
cd post-archiver
pip install -e .
```

## Usage

```
usage: post-archiver [OPTIONS] url [amount]

YouTube Community Posts Scraper

positional arguments:
  url                   YouTube channel community URL
  amount                Amount of posts to get (default: max)

options:
  -h, --help            show this help message and exit
  -c, --get-comments    Get comments from posts (default: False)
  -i, --get-images      Get images from posts (default: False)
  -d, --download-images
                        Download images (requires --get-images)
  -q IMAGE_QUALITY, --image-quality IMAGE_QUALITY
                        Image quality: sd, hd, or all (default: all)
  --proxy PROXY         Proxy file or single proxy string
  -o OUTPUT, --output OUTPUT
                        Output directory (default: current directory)
  -v, --verbose         Show basic progress information
  -t, --trace           Show detailed debug information
  --version             show program's version number and exit

Proxy format:
  Single proxy: <scheme>://<username>:<password>@<host>:<port>
  Proxy file: One proxy per line using the same format
  Supported schemes: socks5, http, https

Amount:
  Specify number of posts to scrape (default: max)
  Use 'max' or any number <= 0 to scrape all posts

Examples:
  post-archiver https://www.youtube.com/@channel/community
  post-archiver https://www.youtube.com/@channel/community 50
  post-archiver -c -i -d -q hd https://www.youtube.com/@channel/community max
  post-archiver --proxy proxies.txt https://www.youtube.com/@channel/community 100
  post-archiver --proxy socks5://username:password@host:port https://www.youtube.com/@channel/community
  post-archiver --proxy http://username:password@host:port https://www.youtube.com/@channel/community
```

## License

MIT License


# YouTube Community Posts Scraper

A Python tool that automatically scrapes posts and links from YouTube channel community tabs using Selenium and BeautifulSoup4.

## 🚀 Features

- Automated scraping of YouTube community posts
- Link extraction and URL expansion
- Proxy support for anonymous scraping
- Headless browser operation
- Infinite scroll handling
- Duplicate post detection
- Automatic cleanup and error handling

## 📋 Prerequisites

- Python 3.7+
- Firefox Browser
- Geckodriver

## 💻 Compatibility

- **Tested on**: Arch Linux
- **Status**: Experimental
- **Note**: This tool has only been tested on Arch Linux. While it should work on other Linux distributions, Windows, and MacOS, you may encounter platform-specific issues that haven't been addressed yet. Please report any compatibility issues through the GitHub issue tracker.

## 🛠️ Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/sadadYes/yt-post-scraper.git
cd yt-post-scraper
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

On Windows:
```bash
venv\Scripts\activate
```

On Unix or MacOS:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure proxy in main.py**
```python
proxy_str = "username:password@host:port"
```

6. **Set target YouTube channel**
```python
driver.get("https://www.youtube.com/@channel_name/community")
```

7. **Run the script**
```bash
python main.py
```

## 📤 Output Example

```
Post content:
Check out my new video: https://www.youtube.com/watch?v=example

Links found:
- New Video: https://www.youtube.com/watch?v=example
--------------------------------------------------
```

## 📦 Dependencies

```
beautifulsoup4>=4.12.0
selenium-wire>=5.1.0
selenium>=4.10.0
packaging>=23.0
setuptools>=67.0.0
```

## 🔧 Advanced Configuration

### Proxy Setup
The script uses Selenium-Wire for proxy support. Configure your proxy in `main.py`:
```python
proxy_str = "username:password@host:port"
```

### Browser Options
Default configuration uses headless Firefox. Modify options in `main.py`:
```python
firefox_options = Options()
firefox_options.add_argument('--headless')  # Remove for visible browser
```

## ⚠️ Error Handling

The script includes:
- Automatic browser cleanup
- Page load wait conditions
- Proxy authentication handling
- Duplicate content detection

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Disclaimer

This tool is for educational purposes only. Users are responsible for complying with YouTube's terms of service and robots.txt policies.

## 🐛 Troubleshooting

- **Proxy Issues**: Verify proxy credentials and connection
- **Selenium Errors**: Ensure Geckodriver is in PATH
- **No Posts Found**: Check channel URL and wait conditions

## 📮 Support

For issues and feature requests, please use the GitHub issue tracker.

## 📝 TODO

### Planned Features
- [ ] Media Handling
  - [ ] Extract posts containing only images
  - [ ] Download/store post images
  - [ ] Handle posts with mixed content (text + images)

- [ ] Post Metadata
  - [ ] Extract post date and time
  - [ ] Get like count
  - [ ] Get comment count

- [ ] Comments
  - [ ] Scrape all comments for each post
  - [ ] Handle nested replies
  - [ ] Extract comment metadata (likes, date, etc.)

- [ ] Data Export
  - [ ] Export data to JSON format
  - [ ] Structured output with post content, media, and metadata

### Future Considerations
- [ ] Rate limiting and throttling
- [ ] Resume capability for interrupted scraping
- [ ] Better error recovery
- [ ] Progress tracking and logging

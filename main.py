from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import json
from datetime import datetime
from urllib.parse import urljoin

firefox_options = Options()
firefox_options.add_argument('--headless')

proxy_str = "username:password@host:port"  # Replace with your proxy
auth, host_port = proxy_str.split('@')
username, password = auth.split(':')
host, port = host_port.split(':')

seleniumwire_options = {
    'proxy': {
        'http': f'http://{username}:{password}@{host}:{port}',
        'https': f'http://{username}:{password}@{host}:{port}'
    }
}

driver = webdriver.Firefox(
    options=firefox_options,
    seleniumwire_options=seleniumwire_options
)

driver.get("https://www.youtube.com/@{youtube_channel}/community") # Replace with your target URL

def get_all_posts():
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    posts_seen = set()
    all_posts_data = []
    
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        post_threads = soup.find_all('ytd-backstage-post-thread-renderer')
        
        for thread in post_threads:
            post_data = {}
            
            # Get post link and timestamp
            timestamp_elem = thread.select_one('div > ytd-backstage-post-renderer > div > div > div > div > yt-formatted-string > a')
            if timestamp_elem:
                post_data['post_url'] = urljoin('https://www.youtube.com', timestamp_elem.get('href', ''))
                post_data['timestamp'] = timestamp_elem.get_text()
            
            # Get post content
            content_elem = thread.select_one('yt-formatted-string#content-text')
            if content_elem:
                text = content_elem.get_text()
                links = content_elem.find_all('a', class_='yt-simple-endpoint')
                
                # Process links in content
                found_links = []
                for link in links:
                    shortened_text = link.get_text()
                    full_url = link.get('href', '')
                    if full_url.startswith('/'):
                        full_url = f'https://www.youtube.com{full_url}'
                    text = text.replace(shortened_text, full_url)
                    found_links.append({
                        'text': shortened_text,
                        'url': full_url
                    })
                
                post_data['content'] = text
                post_data['links'] = found_links
            
            # Get like count
            like_elem = thread.select_one('ytd-comment-action-buttons-renderer > div > span')
            post_data['like_count'] = like_elem.get_text().strip() if like_elem else '0'
            
            # Get comment count
            comment_elem = thread.select_one('ytd-comment-action-buttons-renderer > div > div > ytd-button-renderer > yt-button-shape > a > div > span')
            comment_count = comment_elem.get_text() if comment_elem else '0'
            post_data['comment_count'] = comment_count.split()[0]  # Extract just the number
            
            # Check for duplicate posts
            content_key = post_data.get('content', '')
            if content_key and content_key not in posts_seen:
                posts_seen.add(content_key)
                all_posts_data.append(post_data)
                
                # Print post details (optional)
                print(f"Found post: {post_data['timestamp']}")
                print(f"URL: {post_data['post_url']}")
                print(f"Likes: {post_data['like_count']}")
                print(f"Comments: {post_data['comment_count']}")
                print('-' * 50)
        
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Export to JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    channel_name = driver.current_url.split('@')[1].split('/')[0]
    filename = f'posts_{channel_name}_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'channel': channel_name,
            'scrape_date': datetime.now().isoformat(),
            'posts_count': len(all_posts_data),
            'posts': all_posts_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nExported {len(all_posts_data)} posts to {filename}")
    return all_posts_data

try:
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
    
    get_all_posts()
    
finally:
    driver.quit()


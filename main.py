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
import os
import requests
from urllib.parse import urlparse
from pathlib import Path

class ProxyManager:
    def __init__(self, proxy_file=None, single_proxy=None):
        self.proxies = []
        self.current_index = 0
        
        if proxy_file:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        elif single_proxy:
            self.proxies = [single_proxy]
        
        if not self.proxies:
            raise ValueError("No proxies available. Provide either a proxy file or a single proxy.")
    
    def get_next_proxy(self):
        """Get next proxy in rotation."""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        auth, host_port = proxy.split('@')
        username, password = auth.split(':')
        host, port = host_port.split(':')
        
        return {
            'username': username,
            'password': password,
            'host': host,
            'port': port
        }
    
    def get_seleniumwire_options(self, proxy_info):
        """Generate seleniumwire options for given proxy."""
        return {
            'proxy': {
                'http': f'http://{proxy_info["username"]}:{proxy_info["password"]}@{proxy_info["host"]}:{proxy_info["port"]}',
                'https': f'http://{proxy_info["username"]}:{proxy_info["password"]}@{proxy_info["host"]}:{proxy_info["port"]}'
            },
            'verify_ssl': False,
            'connection_timeout': 30,
            'connection_retries': 3
        }

def create_driver(proxy_manager):
    """Create a new driver with the next proxy."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.set_preference('network.http.connection-timeout', 30)
    
    proxy_info = proxy_manager.get_next_proxy()
    seleniumwire_options = proxy_manager.get_seleniumwire_options(proxy_info)
    
    driver = webdriver.Firefox(
        options=firefox_options,
        seleniumwire_options=seleniumwire_options
    )
    print(f"Using proxy: {proxy_info['host']}:{proxy_info['port']}")
    return driver

def get_post_comments(post_url, driver, proxy_manager, max_retries=3):
    """Get all comments for a specific post with retry logic."""
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                try:
                    driver.quit()
                except:
                    pass
                driver = create_driver(proxy_manager)
            
            driver.get(post_url)
            time.sleep(2)  
            
            comments = []
            
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comment_threads = soup.find_all('ytd-comment-thread-renderer')
            
            for thread in comment_threads:
                comment_data = {}
                
                icon_elem = thread.select_one('ytd-comment-view-model > div > div > a > yt-img-shadow > img')
                if icon_elem and icon_elem.has_attr('src'):
                    icon_url = icon_elem['src']
                    if icon_url.startswith('//'):
                        icon_url = f'https:{icon_url}'
                    comment_data['commenter_icon'] = icon_url
                
                name_elem = thread.select_one('div > div > div > h3 > a > span')
                comment_data['commenter_name'] = name_elem.get_text().strip() if name_elem else ''
                
                timestamp_elem = thread.select_one('div > div > div > div > span > a')
                comment_data['timestamp'] = timestamp_elem.get_text().strip() if timestamp_elem else ''
                
                content_elem = thread.select_one('div > div > ytd-expander > div > yt-attributed-string')
                comment_data['content'] = content_elem.get_text().strip() if content_elem else ''
                
                like_elem = thread.select_one('div > div > ytd-comment-engagement-bar > div > span')
                comment_data['like_count'] = like_elem.get_text().strip() if like_elem else '0'
                
                comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {post_url}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to get comments for {post_url} after {max_retries} attempts")
                return []
            time.sleep(5)

def get_high_res_version(img_url):
    """Convert image URL to high resolution version."""
    if not img_url:
        return None
    base_url = img_url.split('=')[0]
    return f"{base_url}=s2160"

def create_directories(channel_name, timestamp):
    """Create necessary directories for output files."""
    base_dir = Path(f'output/{channel_name}_{timestamp}')
    base_dir.mkdir(parents=True, exist_ok=True)
    
    images_dir = base_dir / 'images'
    images_dir.mkdir(exist_ok=True)
    
    return base_dir, images_dir

def download_image(url, save_path):
    """Download image from URL and save to specified path."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image {url}: {str(e)}")
        return False

def download_post_images(post_data, images_dir, post_index):
    """Download all images for a post and update image paths."""
    downloaded_images = []
    
    for img_index, img in enumerate(post_data['images']):
        filename_base = f"post_{post_index}_img_{img_index}"
        standard_path = images_dir / f"{filename_base}_standard.jpg"
        highres_path = images_dir / f"{filename_base}_highres.jpg"
        
        if download_image(img['standard'], standard_path):
            standard_rel_path = str(standard_path.relative_to(images_dir.parent))
        else:
            standard_rel_path = img['standard']
            
        if download_image(img['high_res'], highres_path):
            highres_rel_path = str(highres_path.relative_to(images_dir.parent))
        else:
            highres_rel_path = img['high_res']
        
        downloaded_images.append({
            'standard': standard_rel_path,
            'high_res': highres_rel_path
        })
    
    return downloaded_images

def get_all_posts(driver, proxy_manager):
    channel_name = driver.current_url.split('@')[1].split('/')[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    base_dir, images_dir = create_directories(channel_name, timestamp)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    channel_icon_elem = soup.select_one('ytd-backstage-post-thread-renderer > div > ytd-backstage-post-renderer > div > div > a > yt-img-shadow > img')
    channel_icon = channel_icon_elem.get('src') if channel_icon_elem else ''
    if channel_icon.startswith('//'):
        channel_icon = f'https:{channel_icon}'
    
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    posts_seen = set()
    all_posts_data = []
    no_new_posts_count = 0
    
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)  
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        post_threads = soup.find_all('ytd-backstage-post-thread-renderer')
        
        initial_posts_count = len(all_posts_data)
        
        for thread in post_threads:
            post_data = {}
            
            timestamp_elem = thread.select_one('div > ytd-backstage-post-renderer > div > div > div > div > yt-formatted-string > a')
            if timestamp_elem:
                post_data['post_url'] = urljoin('https://www.youtube.com', timestamp_elem.get('href', ''))
                post_data['timestamp'] = timestamp_elem.get_text()
            
            content_elem = thread.select_one('yt-formatted-string#content-text')
            if content_elem:
                text = content_elem.get_text()
                links = content_elem.find_all('a', class_='yt-simple-endpoint')
                
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
            else:
                post_data['content'] = None
                post_data['links'] = []
            
            post_data['images'] = []
            
            like_elem = thread.select_one('ytd-comment-action-buttons-renderer > div > span')
            post_data['like_count'] = like_elem.get_text().strip() if like_elem else '0'
            
            comment_elem = thread.select_one('ytd-comment-action-buttons-renderer > div > div > ytd-button-renderer > yt-button-shape > a > div > span')
            comment_count = comment_elem.get_text() if comment_elem else '0'
            post_data['comment_count'] = comment_count.split()[0]
            
            post_url = post_data.get('post_url', '')
            if post_url and post_url not in posts_seen:
                posts_seen.add(post_url)
                all_posts_data.append(post_data)
                print(f"Found post: {post_data['timestamp']}")
                print(f"URL: {post_data['post_url']}")
                print(f"Likes: {post_data['like_count']}")
                print(f"Comments: {post_data['comment_count']}")
                print('-' * 50)
        
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        if len(all_posts_data) == initial_posts_count:
            no_new_posts_count += 1
        else:
            no_new_posts_count = 0
        
        if new_height == last_height and no_new_posts_count >= 3:
            break
            
        last_height = new_height
        print(f"Found {len(all_posts_data)} posts so far...")
    
    print(f"\nFound {len(all_posts_data)} posts, now collecting images...")
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    for post_data in all_posts_data:
        post_url = post_data['post_url']
        post_elem = driver.find_element(By.CSS_SELECTOR, f'a[href*="{post_url.split("/")[-1]}"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", post_elem)
        time.sleep(0.5)  
        
        post_thread = BeautifulSoup(post_elem.find_element(By.XPATH, "ancestor::ytd-backstage-post-thread-renderer").get_attribute('outerHTML'), 'html.parser')
        
        single_image = post_thread.select_one('div#content-attachment ytd-backstage-image-renderer img#img')
        if single_image and single_image.has_attr('src'):
            img_url = single_image['src']
            if img_url.startswith('//'):
                img_url = f'https:{img_url}'
            post_data['images'].append({
                'standard': img_url,
                'high_res': get_high_res_version(img_url)
            })
        
        multi_images = post_thread.select('div#content-attachment ytd-post-multi-image-renderer img#img')
        for img in multi_images:
            if img.has_attr('src'):
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = f'https:{img_url}'
                post_data['images'].append({
                    'standard': img_url,
                    'high_res': get_high_res_version(img_url)
                })
    
    print(f"\nCollected images, now gathering comments...")
    
    total_posts = len(all_posts_data)
    for index, post_data in enumerate(all_posts_data, 1):
        if post_data['images']:
            post_data['images'] = download_post_images(post_data, images_dir, index)
        
        post_url = post_data['post_url']
        print(f"Getting comments for post {index}/{total_posts}: {post_url}")
        
        comments = get_post_comments(
            post_url=post_url,
            driver=driver,
            proxy_manager=proxy_manager
        )
        post_data['comments'] = comments
        print(f"Found {len(comments)} comments")
        
        if index % 5 == 0:
            temp_filename = base_dir / f'posts_{channel_name}_temp_{timestamp}.json'
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'channel': channel_name,
                    'channel_icon': channel_icon,
                    'scrape_date': datetime.now().isoformat(),
                    'scrape_timestamp': int(datetime.now().timestamp()),
                    'posts_count': len(all_posts_data),
                    'posts': all_posts_data
                }, f, ensure_ascii=False, indent=2)
            print(f"Saved progress to {temp_filename}")
    
    filename = base_dir / f'posts_{channel_name}_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'channel': channel_name,
            'channel_icon': channel_icon,
            'scrape_date': datetime.now().isoformat(),
            'scrape_timestamp': int(datetime.now().timestamp()),
            'posts_count': len(all_posts_data),
            'posts': all_posts_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nExported {len(all_posts_data)} posts to {filename}")
    return all_posts_data

try:
    proxy_manager = ProxyManager(proxy_file='proxies.txt') # Use proxies from file
except:
    proxy_str = "username:password@host:port"
    proxy_manager = ProxyManager(single_proxy=proxy_str) # Use single proxy

driver = create_driver(proxy_manager)

try:
    driver.get("https://www.youtube.com/@{youtube_channel}/community")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
    
    get_all_posts(driver=driver, proxy_manager=proxy_manager)
    
finally:
    driver.quit()


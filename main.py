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
        if new_height == last_height:
            break
        last_height = new_height
    
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
            post_data['images'].append(img_url)
        
        multi_images = post_thread.select('div#content-attachment ytd-post-multi-image-renderer img#img')
        for img in multi_images:
            if img.has_attr('src'):
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = f'https:{img_url}'
                post_data['images'].append(img_url)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    channel_name = driver.current_url.split('@')[1].split('/')[0]
    filename = f'posts_{channel_name}_{timestamp}.json'
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    channel_icon_elem = soup.select_one('ytd-backstage-post-thread-renderer > div > ytd-backstage-post-renderer > div > div > a > yt-img-shadow > img')
    channel_icon = channel_icon_elem.get('src') if channel_icon_elem else ''
    if channel_icon.startswith('//'):
        channel_icon = f'https:{channel_icon}'
    
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
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
    
    get_all_posts()
    
finally:
    driver.quit()


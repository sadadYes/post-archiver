from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys

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
    
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        posts = soup.find_all('yt-formatted-string', {'id': 'content-text'})
        
        for post in posts:
            text = post.get_text()
            
            links = post.find_all('a', class_='yt-simple-endpoint')
            
            for link in links:
                shortened_text = link.get_text()
                full_url = link.get('href', '')
                if full_url.startswith('/'):
                    full_url = f'https://www.youtube.com{full_url}'
                text = text.replace(shortened_text, full_url)
            
            if text not in posts_seen:
                posts_seen.add(text)
                print("Post content:")
                print(text)
                print("\nLinks found:")
                for link in links:
                    shortened_text = link.get_text()
                    full_url = link.get('href', '')
                    if full_url.startswith('/'):
                        full_url = f'https://www.youtube.com{full_url}'
                    print(f"- {shortened_text}: {full_url}")
                print('-' * 50)
        
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        if new_height == last_height:
            break
            
        last_height = new_height

try:
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
    
    get_all_posts()
    
finally:
    driver.quit()

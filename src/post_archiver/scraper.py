"""Core scraping functionality for YouTube Community Posts"""
import json
import time
import logging
import requests
from datetime import datetime
from urllib.parse import urljoin
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import expect

from .browser import create_driver
from .utils import create_directories, download_image

# Move all the functions from your main file here
def get_post_comments(post_url, driver, proxy_manager, max_retries=3):
    """Get all comments for a specific post with retry logic."""
    browser_type = getattr(driver, 'browser_type', 'chromium')  # Get browser type or default to chromium
    
    for attempt in range(max_retries):
        try:
            # Create a new driver with next proxy if this is a retry
            if attempt > 0:
                try:
                    driver.quit()
                except:
                    pass
                driver = create_driver(proxy_manager, browser_type=browser_type)
            
            driver.goto(post_url)
            driver.wait_for_timeout(2000)  # Wait for initial load
            
            comments = []
            
            # Scroll to load all comments
            last_height = driver.evaluate("document.documentElement.scrollHeight")
            while True:
                driver.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                driver.wait_for_timeout(2000)
                
                new_height = driver.evaluate("document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Parse comments
            soup = BeautifulSoup(driver.content(), 'html.parser')
            comment_threads = soup.find_all('ytd-comment-thread-renderer')
            
            for thread in comment_threads:
                comment_data = {}
                
                # Get commenter icon
                icon_elem = thread.select_one('ytd-comment-view-model > div > div > a > yt-img-shadow > img')
                if icon_elem and icon_elem.has_attr('src'):
                    icon_url = icon_elem['src']
                    if icon_url.startswith('//'):
                        icon_url = f'https:{icon_url}'
                    comment_data['commenter_icon'] = icon_url
                
                # Get commenter name
                name_elem = thread.select_one('div > div > div > h3 > a > span')
                comment_data['commenter_name'] = name_elem.get_text().strip() if name_elem else ''
                
                # Get comment timestamp
                timestamp_elem = thread.select_one('div > div > div > div > span > a')
                comment_data['timestamp'] = timestamp_elem.get_text().strip() if timestamp_elem else ''
                
                # Get comment content
                content_elem = thread.select_one('div > div > ytd-expander > div > yt-attributed-string')
                comment_data['content'] = content_elem.get_text().strip() if content_elem else ''
                
                # Get like count
                like_elem = thread.select_one('div > div > ytd-comment-engagement-bar > div > span')
                comment_data['like_count'] = like_elem.get_text().strip() if like_elem else '0'
                
                comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {post_url}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to get comments for {post_url} after {max_retries} attempts")
                return []
            driver.wait_for_timeout(5000)

def get_high_res_version(img_url):
    """Convert image URL to high resolution version."""
    if not img_url:
        return None
    base_url = img_url.split('=')[0]
    return f"{base_url}=s2160"

def create_directories(channel_name, timestamp, base_dir=None, create_images_dir=False):
    """Create necessary directories for output files."""
    try:
        # Use specified directory or current working directory
        parent_dir = base_dir if base_dir else Path.cwd()
        
        # Create channel-specific directory
        channel_dir = parent_dir / f'{channel_name}_{timestamp}'
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        # Create images directory only if needed
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
        print(f"Error downloading image {url}: {str(e)}")
        return False

def download_post_images(post_data, images_dir, post_index):
    """Download all images for a post and update image paths."""
    downloaded_images = []
    
    for img_index, img in enumerate(post_data['images']):
        # Create filenames for both versions
        filename_base = f"post_{post_index}_img_{img_index}"
        standard_path = images_dir / f"{filename_base}_standard.jpg"
        highres_path = images_dir / f"{filename_base}_highres.jpg"
        
        # Download standard version
        if download_image(img['standard'], standard_path):
            # Keep the original URL in the JSON
            standard_url = img['standard']
        else:
            standard_url = img['standard']
            
        # Download high-res version
        if download_image(img['high_res'], highres_path):
            # Keep the original URL in the JSON
            highres_url = img['high_res']
        else:
            highres_url = img['high_res']
        
        downloaded_images.append({
            'standard': standard_url,
            'high_res': highres_url
        })
    
    return downloaded_images

def get_channel_icon(driver):
    """Get channel icon URL from the page."""
    soup = BeautifulSoup(driver.content(), 'html.parser')
    channel_icon_elem = soup.select_one('ytd-backstage-post-thread-renderer > div > ytd-backstage-post-renderer > div > div > a > yt-img-shadow > img')
    channel_icon = channel_icon_elem.get('src') if channel_icon_elem else ''
    if channel_icon.startswith('//'):
        channel_icon = f'https:{channel_icon}'
    return channel_icon

def get_all_posts(driver, proxy_manager, get_comments=False, get_images=False, 
                  download_images=False, image_quality='all', output_dir=None, 
                  verbose=False, trace=False, max_posts=float('inf')):
    """Get all posts with specified options."""
    all_posts_data = []
    posts_seen = set()
    no_new_posts_count = 0
    should_break = False
    
    # Get channel info
    channel_name = driver.url.split('@')[1].split('/')[0]
    channel_icon = get_channel_icon(driver)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create directories using specified output directory
    base_dir, images_dir = create_directories(
        channel_name, 
        timestamp, 
        output_dir,
        create_images_dir=download_images
    )
    
    # Wait for initial post load
    driver.wait_for_selector("ytd-backstage-post-thread-renderer")
    
    # Initialize last_height before the loop
    last_height = driver.evaluate("document.documentElement.scrollHeight")
    
    while True:
        initial_posts_count = len(all_posts_data)
        
        # Scroll down
        driver.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        driver.wait_for_timeout(2000)  # Wait for content to load
        
        # Get all post threads
        post_threads = driver.query_selector_all("ytd-backstage-post-thread-renderer")
        
        # Process posts
        for thread in post_threads:
            # Convert element to BeautifulSoup object
            thread_html = thread.inner_html()
            soup_thread = BeautifulSoup(thread_html, 'html.parser')
            
            post_data = {}
            
            # Get post link and timestamp
            timestamp_elem = soup_thread.select_one('div > ytd-backstage-post-renderer > div > div > div > div > yt-formatted-string > a')
            if timestamp_elem:
                post_data['post_url'] = urljoin('https://www.youtube.com', timestamp_elem.get('href', ''))
                post_data['timestamp'] = timestamp_elem.get_text()
            
            # Get post content
            content_elem = soup_thread.select_one('yt-formatted-string#content-text')
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
            
            # Initialize images list with both versions
            post_data['images'] = []
            
            # Get like count
            like_elem = soup_thread.select_one('ytd-comment-action-buttons-renderer > div > span')
            post_data['like_count'] = like_elem.get_text().strip() if like_elem else '0'
            
            # Get comment count
            comment_elem = soup_thread.select_one('ytd-comment-action-buttons-renderer > div > div > ytd-button-renderer > yt-button-shape > a > div > span')
            comment_count = comment_elem.get_text() if comment_elem else '0'
            post_data['comment_count'] = comment_count.split()[0]
            
            # Check for duplicate posts using URL
            post_url = post_data.get('post_url', '')
            if post_url and post_url not in posts_seen:
                posts_seen.add(post_url)
                all_posts_data.append(post_data)
                if verbose or trace:
                    print(f"Found post: {post_data['timestamp']}")
                    print(f"URL: {post_data['post_url']}")
                    print(f"Likes: {post_data['like_count']}")
                    print(f"Comments: {post_data['comment_count']}")
                    print('-' * 50)
                
                if len(all_posts_data) >= max_posts:
                    print(f"\nReached requested amount of {max_posts} posts")
                    should_break = True
                    break
        
        if should_break:
            break
            
        # Check scroll progress
        new_height = driver.evaluate("document.documentElement.scrollHeight")
        
        # Check if we got any new posts
        if len(all_posts_data) == initial_posts_count:
            no_new_posts_count += 1
        else:
            no_new_posts_count = 0
        
        # If height didn't change and we haven't found new posts in 3 attempts, we're done
        if new_height == last_height and no_new_posts_count >= 3:
            break
            
        last_height = new_height
        if trace:
            print(f"Found {len(all_posts_data)} posts so far...")
            print(f"Current height: {new_height}, Last height: {last_height}")
            print(f"No new posts count: {no_new_posts_count}")
        elif verbose:
            print(f"Scrolling... ({len(all_posts_data)} posts)")
    
    print(f"\nCollected {len(all_posts_data)} posts, now processing...")
    
    # Second pass - collect images
    if get_images:
        print("\nCollecting images...")
        driver.evaluate("window.scrollTo(0, 0)")
        driver.wait_for_timeout(2000)
        
        for post_data in all_posts_data:
            # Scroll to the post
            post_url = post_data['post_url']
            post_elem = driver.query_selector(f'a[href*="{post_url.split("/")[-1]}"]')
            if post_elem:
                driver.evaluate("element => element.scrollIntoView(true)", post_elem)
                driver.wait_for_timeout(500)  # Small delay to let images load
                
                # Get updated HTML for this post
                post_thread = BeautifulSoup(
                    post_elem.evaluate("element => element.closest('ytd-backstage-post-thread-renderer').outerHTML"),
                    'html.parser'
                )
                
                # Initialize images list
                post_data['images'] = []
                
                # Get multiple images first (if any)
                multi_images = post_thread.select('div#content-attachment ytd-post-multi-image-renderer img#img')
                if multi_images:
                    for img in multi_images:
                        if img.has_attr('src'):
                            img_url = img['src']
                            if img_url.startswith('//'):
                                img_url = f'https:{img_url}'
                            post_data['images'].append({
                                'standard': img_url,
                                'high_res': get_high_res_version(img_url)
                            })
                else:
                    # Only check for single image if no multiple images were found
                    single_image = post_thread.select_one('div#content-attachment ytd-backstage-image-renderer img#img')
                    if single_image and single_image.has_attr('src'):
                        img_url = single_image['src']
                        if img_url.startswith('//'):
                            img_url = f'https:{img_url}'
                        post_data['images'].append({
                            'standard': img_url,
                            'high_res': get_high_res_version(img_url)
                        })
    
    # Third pass - collect comments and download images
    total_posts = len(all_posts_data)
    for index, post_data in enumerate(all_posts_data, 1):
        # Download images if requested
        if download_images and post_data.get('images') and images_dir:
            post_data['images'] = download_post_images(post_data, images_dir, index)
        
        # Get comments if requested
        if get_comments:
            if index == 1:  # Only print this once at the start
                print("\nCollecting comments...")
            
            post_url = post_data['post_url']
            if verbose:
                print(f"Getting comments for post {index}/{total_posts}: {post_url}")
            else:
                print(f"Getting comments for post {index}/{total_posts}")
            
            comments = get_post_comments(
                post_url=post_url,
                driver=driver,
                proxy_manager=proxy_manager
            )
            post_data['comments'] = comments
            if verbose:
                print(f"Found {len(comments)} comments")
        
        # Save progress every 5 posts
        if index % 5 == 0:
            temp_filename = base_dir / f'posts_{channel_name}_temp_{timestamp}.json'
            try:
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'channel': channel_name,
                        'channel_icon': channel_icon,
                        'scrape_date': datetime.now().isoformat(),
                        'scrape_timestamp': int(datetime.now().timestamp()),
                        'posts_count': len(all_posts_data),
                        'posts': all_posts_data[:index]  # Only save processed posts
                    }, f, ensure_ascii=False, indent=2)
                if verbose:
                    print(f"\nSaved progress ({index}/{total_posts} posts) to {temp_filename}")
            except Exception as e:
                print(f"Error saving progress: {str(e)}")
            
            # Add a small delay to ensure messages are printed in order
            driver.wait_for_timeout(100)
    
    # Always save final JSON file
    filename = base_dir / f'posts_{channel_name}_{timestamp}.json'
    try:
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
    except Exception as e:
        print(f"Error saving final JSON: {str(e)}")
    
    return all_posts_data

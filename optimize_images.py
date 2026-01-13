import os
import re
import hashlib
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

# Configuration
HTML_FILES = ['model1.html', 'model2.html', 'model3.html']
ASSETS_DIR = 'assets/img'
MAX_WIDTH = 1920
QUALITY = 80

# Ensure assets directory exists
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

def download_and_optimize(url):
    try:
        # Create a filename based on the URL hash to avoid duplicates
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        filename = f"{url_hash}.webp"
        filepath = os.path.join(ASSETS_DIR, filename)

        # Return existing path if already downloaded
        if os.path.exists(filepath):
            return f"{ASSETS_DIR}/{filename}"

        # Download image
        print(f"Downloading: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Open and optimize
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary (e.g. RGBA to RGB for JPEG, but WebP supports RGBA)
        # WebP handles transparency, so we can keep RGBA if present.
        
        # Resize if too large
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

        # Save as WebP
        img.save(filepath, 'WEBP', quality=QUALITY)
        print(f"Saved: {filepath}")
        
        return f"{ASSETS_DIR}/{filename}"
        
    except Exception as e:
        print(f"Failed to optimize {url}: {str(e)}")
        return None

def process_html(file_path):
    print(f"\nProcessing {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find image URLs
    # Matches src="..." and url('...')
    # We look for http/https URLs only
    
    # 1. img tags with src
    # Pattern: src=["'](http[^"']+)["']
    img_pattern = r'src=["\'](https?://[^"\']+)["\']'
    
    # 2. css background-image: url('...')
    # Pattern: url\(['"]?(http[^'")]+)['"]?\)
    css_pattern = r'url\([\'"]?(https?://[^\'"\)]+)[\'"]?\)'
    
    # Collect all unique URLs
    urls = set()
    urls.update(re.findall(img_pattern, content))
    urls.update(re.findall(css_pattern, content))
    
    print(f"Found {len(urls)} external images.")
    
    replacements = {}
    
    for url in urls:
        # Skip if already local (though regex expects http)
        # Check against exclusions if needed (e.g. analytics pixels)
        
        new_path = download_and_optimize(url)
        if new_path:
            replacements[url] = new_path

    # Perform replacements using regex to be safe with structure
    # We iterate over the *original* content to replace literal strings
    # But doing simple string replace might be dangerous if URL appears in text users see.
    # However, these are long URLs, unlikely to appear in text.
    # Better to use regex substitution to target only src/url contexts.
    
    new_content = content
    
    # Replace in src attributes
    def replace_src(match):
        url = match.group(1)
        if url in replacements:
            return f'src="{replacements[url]}"'
        return match.group(0)
    
    new_content = re.sub(img_pattern, replace_src, new_content)

    # Replace in url()
    def replace_url(match):
        url = match.group(1)
        if url in replacements:
            return f"url('{replacements[url]}')"
        return match.group(0)

    new_content = re.sub(css_pattern, replace_url, new_content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")

if __name__ == "__main__":
    for html_file in HTML_FILES:
        process_html(html_file)

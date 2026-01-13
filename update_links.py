import os
import re

# Configuration
HTML_FILES = ['model1.html', 'model2.html', 'model3.html']
NEW_WHATSAPP_LINK = 'https://wa.link/1nxmx6'

def process_html(file_path):
    print(f"\nProcessing {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find existing WhatsApp links
    # Matches href="https://wa.me/..." or href="https://api.whatsapp.com/..."
    # Also handles simple phone numbers if used in wa.me
    
    # Pattern 1: wa.me
    # href=["'](https?://wa\.me/[^"']+)["']
    # Pattern 2: api.whatsapp.com
    # href=["'](https?://api\.whatsapp\.com/[^"']+)["']
    
    # We want to replace the whole URL with NEW_WHATSAPP_LINK
    
    whatsapp_pattern = r'href=["\'](https?://(wa\.me|api\.whatsapp\.com)/[^"\']+)["\']'
    
    # Also catch simple "wa.me/" without https if present (though usually browsers require protocol)
    
    count = 0
    
    def replace_link(match):
        nonlocal count
        count += 1
        # Maintain the quote style used in original
        quote = match.group(0)[5] # href=" or href='
        return f'href={quote}{NEW_WHATSAPP_LINK}{quote}'
    
    new_content = re.sub(whatsapp_pattern, replace_link, content)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {count} links in {file_path}")
    else:
        print(f"No WhatsApp links found in {file_path}")

if __name__ == "__main__":
    for html_file in HTML_FILES:
        process_html(html_file)

import os
import glob
import re

html_files = glob.glob(r'c:\Users\Musa\Desktop\Projects\DiabetiCare\templates\**\*.html', recursive=True)

logo_html = '''<img src="{{ url_for('static', filename='images/logo.jpeg') }}" alt="DiabetiCare Logo" class="welcome-logo" style="width: 80px; height: 80px; object-fit: cover; border-radius: 50%; margin: 0 auto var(--space-md); display: block; box-shadow: 0 4px 6px -1px var(--shadow-color);">'''

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # Match <div class="welcome-logo" ...>...</div>
    new_content, count = re.subn(r'<div class="welcome-logo"[^>]*>.*?</div>', logo_html, content, flags=re.DOTALL)
    if count > 0:
        content = new_content
        modified = True
    
    # Also update base.html logo
    if 'base.html' in file.replace('\\', '/'):
        new_content, count = re.subn(r'<span class="logo-icon">.*?</span>', 
                         r'''<img src="{{ url_for('static', filename='images/logo.jpeg') }}" alt="Logo" class="logo-icon" style="height: 28px; width: 28px; border-radius: 50%; object-fit: cover; margin-right: var(--space-xs);">''', 
                         content, flags=re.DOTALL)
        if count > 0:
            content = new_content
            modified = True
    
    if modified:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(file)}")

print("Done updating logos")

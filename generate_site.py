import os
import re
import datetime
from bs4 import BeautifulSoup

# Configuration
INPUT_DIR = "."
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"

def find_latest_favorites_file(directory):
    files = [f for f in os.listdir(directory) if f.startswith("favorites_") and f.endswith(".html")]
    if not files:
        return None
    # Sort by date (assuming YYYY_MM_DD format in filename)
    files.sort(reverse=True)
    return os.path.join(directory, files[0])

def parse_favorites(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    
    # Analyze structure. Netscape bookmarks are nested DL/DT based.
    # We want to flatten it a bit or keep the main sections.
    # Let's target the H3 headers which denote folders.
    
    categories = []
    
    # Finding all top-level H3s or main sections might be tricky because of nesting.
    # A simple approach for a "Dashboard" is to find all H3s and their immediate links.
    # Or, we can just grab everything into specific "Zones" if the user has organized them.
    # Given the user's file, let's try to extract top-level folders or just group by Folder Name.
    
    # We will traverse all <dt> that have an <h3> child.
    
    for dt in soup.find_all("dt"):
        h3 = dt.find("h3")
        if h3:
            category_name = h3.get_text()
            # The next sibling of the h3's parent dt usually contains the <dl> with links
            dl = dt.find("dl")
            if not dl:
                # sometimes structural variations
                 dl = dt.find_next_sibling("dl")
            
            if dl:
                links = []
                for link in dl.find_all("a"):
                     # We assume flat list inside folders for simplicity on the dashboard
                     # If we want full recursion it gets complex for a static single-page dashboard.
                     # Let's just grab all links inside this category (recursively or not).
                     # For a clean dashboard, let's grab specific links.
                     
                     title = link.get_text()
                     url = link.get("href")
                     icon = link.get("icon", "")
                     add_date = link.get("add_date")
                     
                     if url and not url.startswith("place:"): # skip smart bookmarks
                         links.append({
                             "title": title,
                             "url": url,
                             "icon": icon
                         })
                
                if links:
                    categories.append({
                        "name": category_name,
                        "links": links
                    })

    return categories

def generate_html(categories, template_path, output_path):
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    html_content = ""
    
    for cat in categories:
        html_content += f'<div class="category-section">\n'
        html_content += f'    <h2 class="category-title">{cat["name"]}</h2>\n'
        html_content += f'    <div class="bookmark-grid">\n'
        
        for link in cat["links"]:
            # Default icon if none provided
            icon_html = ""
            if link["icon"]:
                 icon_html = f'<img src="{link["icon"]}" alt="">'
            else:
                 # Generate a simple SVG or letter based icon
                 first_char = link["title"][0].upper() if link["title"] else "?"
                 icon_html = f'<div style="font-weight:bold; font-size:1.2rem;">{first_char}</div>'

            html_content += f'''
            <a href="{link["url"]}" class="bookmark-card" target="_blank">
                <div class="icon-wrapper">
                    {icon_html}
                </div>
                <div class="bookmark-info">
                    <div class="bookmark-name">{link["title"]}</div>
                    <div class="bookmark-url">{link["url"]}</div>
                </div>
            </a>
            '''
        
        html_content += '    </div>\n</div>\n'
        
    final_html = template.replace('<!-- CONTENT_PLACEHOLDER -->', html_content)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_html = final_html.replace('<!-- TIME_PLACEHOLDER -->', now)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Successfully generated {output_path}")

def main():
    latest_file = find_latest_favorites_file(INPUT_DIR)
    if not latest_file:
        print("No favorites_*.html file found!")
        return
        
    categories = parse_favorites(latest_file)
    generate_html(categories, TEMPLATE_FILE, OUTPUT_FILE)

if __name__ == "__main__":
    main()

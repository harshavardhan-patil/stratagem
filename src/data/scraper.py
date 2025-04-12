from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from src.config import RAW_DATA_DIR

def scrape_case_study(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Load the page
    driver.get(url)
    # Wait for page to fully load
    time.sleep(5)
    
    # Get the page source and parse with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    # Extract title
    title = soup.find('h1')
    if title:
        title = title.text.strip()
    else:
        # Fallback to looking for the h1 in other ways
        title = soup.select_one('.hdn, h1, .fs-4')
        if title:
            title = title.text.strip()
        else:
            title = "Case Study"
    
    # Extract the case study content
    # First try to find the table of contents to use as a guide
    toc = soup.find(id='toc')
    content_sections = []
    
    if toc:
        # Get all section anchors from TOC
        section_links = toc.find_all('a')
        section_ids = [link.get('href', '').replace('#', '') for link in section_links if link.get('href', '').startswith('#')]
        
        # Extract content for each section
        for section_id in section_ids:
            section = soup.find(id=section_id) or soup.find('a', {'name': section_id})
            if section:
                # Find the section heading
                heading = section.find_next(['h2', 'h3', 'h4']) 
                if heading:
                    content_sections.append(f"\n{heading.text.strip()}\n")
                    
                    # Extract all paragraphs until the next heading or section
                    current = heading.find_next(['p', 'ul', 'ol', 'div'])
                    while current and current.name not in ['h2', 'h3', 'h4'] and not (current.name == 'a' and current.get('name') in section_ids):
                        if current.name in ['p', 'li']:
                            text = current.text.strip()
                            if text and not text.startswith("Preview") and "Add to Cart" not in text:
                                content_sections.append(text)
                        elif current.name == 'ul' or current.name == 'ol':
                            for li in current.find_all('li'):
                                text = li.text.strip()
                                if text:
                                    content_sections.append(f"- {text}")
                        current = current.find_next()
    else:
        # If no TOC, try to extract the main content based on structure
        main_content = soup.find('div', {'class': 'section'}) or soup.find('div', {'class': 'lh-lg'})
        
        if main_content:
            for elem in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
                if elem.name in ['h2', 'h3']:
                    content_sections.append(f"\n{elem.text.strip()}\n")
                elif elem.name == 'p':
                    text = elem.text.strip()
                    if text and not text.startswith("Preview") and "Add to Cart" not in text:
                        content_sections.append(text)
                elif elem.name in ['ul', 'ol']:
                    for li in elem.find_all('li'):
                        text = li.text.strip()
                        if text:
                            content_sections.append(f"- {text}")
        else:
            # Final fallback: grab all paragraphs in the main container
            main_container = soup.find('div', {'class': 'container'})
            if main_container:
                for p in main_container.find_all('p'):
                    text = p.text.strip()
                    if text and len(text) > 50 and not text.startswith("Preview") and "Add to Cart" not in text:
                        content_sections.append(text)
    
    # For the summary/key findings section at the end
    summary_section = soup.find(id='summary') or soup.find('a', {'name': 'summary'})
    if summary_section:
        heading = summary_section.find_next(['h2', 'h3'])
        if heading:
            content_sections.append(f"\n{heading.text.strip()}\n")
            
            # Extract summary paragraphs
            for p in summary_section.find_next_siblings(['p', 'ul', 'div']):
                if p.name == 'p':
                    text = p.text.strip()
                    if text and not text.startswith("Preview") and "Add to Cart" not in text:
                        content_sections.append(text)
                elif p.name == 'ul':
                    for li in p.find_all('li'):
                        text = li.text.strip()
                        if text:
                            content_sections.append(f"- {text}")
    
    # Clean up content by removing promotional text, navigation elements, etc.
    cleaned_content = []
    for text in content_sections:
        # Skip short promotional snippets, navigation, footer links, etc.
        if (len(text) < 30 and not text.startswith('\n')) or 'Read Insights' in text or 'Download this' in text:
            continue
        
        # Skip common promotional phrases or sections
        skip_phrases = [
            "FlevyPro provides", "Download our", "FREE DOWNLOAD", 
            "Browse by Function", "© Copyright", "Customer Testimonials"
        ]
        
        if any(phrase in text for phrase in skip_phrases):
            continue
            
        cleaned_content.append(text)
    
    # Combine cleaned content into a single string
    full_content = f"Title: {title}\n\nSource: {url}\n\n" + "\n".join(cleaned_content)
    
    return full_content

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Content saved to {filename}")

def scrape_multiple_case_studies(urls, output_folder=RAW_DATA_DIR):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, url in enumerate(urls):
        try:
            print(f"Scraping case study {i+1}/{len(urls)}: {url}")
            content = scrape_case_study(url)
            
            # Generate filename from URL
            url_parts = url.split('/')
            filename = url_parts[-1] if url_parts[-1] else f"case_study_{i+1}"
            filename = f"{filename}.txt"
            
            save_to_file(content, os.path.join(output_folder, filename))
        except Exception as e:
            print(f"Error scraping {url}: {e}")

# Example usage
if __name__ == "__main__":
    # List of case study URLs to scrape
    case_study_urls = [
        "https://flevy.com/topic/growth-strategy/case-growth-strategy-southeast-asia-boutique-hotel-chain",
        "https://flevy.com/topic/growth-strategy/case-telecom-customer-experience-transformation-digital-era",
    ]
    
    scrape_multiple_case_studies(case_study_urls)
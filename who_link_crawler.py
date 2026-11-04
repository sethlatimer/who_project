import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WHOLinkCrawler:
    def __init__(self, base_url="https://www.who.int", output_file="who_links.txt"):
        self.base_url = base_url
        self.output_file = output_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Track visited URLs to avoid duplicates
        self.visited_urls = set()
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def is_valid_url(self, url):
        """Check if URL belongs to WHO domain"""
        parsed_url = urlparse(url)
        return parsed_url.netloc == urlparse(self.base_url).netloc
    
    def extract_links(self, url):
        """Extract all links from a page"""
        content = self.get_page_content(url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            full_url = urljoin(self.base_url, href)
            
            # Only process links that belong to WHO domain
            if self.is_valid_url(full_url):
                links.append(full_url)
        
        return links
    
    def crawl_page(self, url, max_depth=2, current_depth=0):
        """Recursively crawl pages up to a certain depth"""
        if current_depth > max_depth or url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        logger.info(f"Crawling: {url}")
        
        links = self.extract_links(url)
        all_links = links[:]
        
        # Recursively crawl linked pages (but not too deep)
        if current_depth < max_depth:
            for link in links[:10]:  # Limit to first 10 links per page to avoid excessive crawling
                try:
                    # Add delay between requests
                    time.sleep(0.5)
                    all_links.extend(self.crawl_page(link, max_depth, current_depth + 1))
                except Exception as e:
                    logger.error(f"Error crawling {link}: {e}")
        
        return all_links
    
    def save_links(self, links):
        """Save links to file"""
        with open(self.output_file, 'w') as f:
            for link in sorted(set(links)):
                f.write(f"{link}\n")
        logger.info(f"Saved {len(set(links))} links to {self.output_file}")
    
    def crawl_and_save(self, start_urls=None, max_depth=2):
        """Crawl WHO website and save all links"""
        if not start_urls:
            start_urls = [
                "https://www.who.int/data",
                "https://www.who.int/health-topics",
                "https://www.who.int/publications",
                "https://www.who.int/reports"
            ]
        
        all_links = []
        
        for start_url in start_urls:
            logger.info(f"Starting crawl from: {start_url}")
            links = self.crawl_page(start_url, max_depth)
            all_links.extend(links)
        
        # Remove duplicates and save
        unique_links = list(set(all_links))
        self.save_links(unique_links)
        
        return unique_links

def main():
    """Main function to run the crawler"""
    crawler = WHOLinkCrawler()
    
    try:
        # Start crawling
        links = crawler.crawl_and_save(max_depth=1)
        print(f"Found and saved {len(links)} links")
        
    except KeyboardInterrupt:
        logger.info("Crawling process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

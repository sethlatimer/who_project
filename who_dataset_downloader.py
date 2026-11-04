import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WHODataDownloader:
    def __init__(self, base_url="https://www.who.int", download_dir="who_datasets"):
        self.base_url = base_url
        self.download_dir = download_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def find_pdf_links(self, url):
        """Find all PDF links on a page"""
        content = self.get_page_content(url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        pdf_links = []
        
        # Find all links that end with .pdf
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(self.base_url, href)
                pdf_links.append(full_url)
        
        return pdf_links
    
    def find_dataset_links(self, url):
        """Find dataset links on WHO pages"""
        content = self.get_page_content(url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        dataset_links = []
        
        # Look for common dataset patterns
        # Search in various sections that might contain datasets
        sections = soup.find_all(['div', 'section', 'article'])
        
        for section in sections:
            # Look for links with dataset-related text
            for link in section.find_all('a', href=True):
                href = link['href']
                text = link.get_text().lower()
                
                # Common dataset keywords
                dataset_keywords = ['dataset', 'data', 'statistics', 'report', 'survey']
                if any(keyword in text for keyword in dataset_keywords):
                    full_url = urljoin(self.base_url, href)
                    dataset_links.append(full_url)
        
        return dataset_links
    
    def download_file(self, url, filename=None):
        """Download a file from URL"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # If no filename provided, extract from URL
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"download_{int(time.time())}.pdf"
            
            filepath = os.path.join(self.download_dir, filename)
            
            # Write file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    def load_links_from_file(self, links_file="who_links.txt"):
        """Load links from a file"""
        if not os.path.exists(links_file):
            logger.warning(f"Links file {links_file} not found")
            return []
        
        with open(links_file, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Loaded {len(links)} links from {links_file}")
        return links
    
    def search_who_datasets(self, search_terms=None, use_cached_links=False):
        """Search for datasets on WHO website"""
        logger.info("Searching WHO datasets...")
        
        # If using cached links, load them from file
        if use_cached_links:
            links = self.load_links_from_file()
            if not links:
                # Fallback to default pages if no cached links
                links = [
                    "https://www.who.int/data",
                    "https://www.who.int/health-topics",
                    "https://www.who.int/publications",
                    "https://www.who.int/reports"
                ]
        else:
            # Base WHO pages to search
            links = [
                "https://www.who.int/data",
                "https://www.who.int/health-topics",
                "https://www.who.int/publications",
                "https://www.who.int/reports"
            ]
        
        all_links = []
        
        for page in links:
            logger.info(f"Scanning: {page}")
            
            # Get PDF links
            pdf_links = self.find_pdf_links(page)
            all_links.extend(pdf_links)
            
            # Get dataset links
            dataset_links = self.find_dataset_links(page)
            all_links.extend(dataset_links)
        
        # Remove duplicates
        unique_links = list(set(all_links))
        logger.info(f"Found {len(unique_links)} unique links")
        
        return unique_links
    
    def download_datasets(self, search_terms=None, use_cached_links=False):
        """Download all found datasets"""
        logger.info("Starting dataset download process...")
        
        # Find all links
        links = self.search_who_datasets(search_terms, use_cached_links)
        
        if not links:
            logger.warning("No datasets found to download")
            return
        
        downloaded_files = []
        
        for i, link in enumerate(links):
            logger.info(f"Processing {i+1}/{len(links)}: {link}")
            
            # Add delay to be respectful to server
            time.sleep(1)
            
            # Try to download the file
            filename = None
            if link.endswith('.pdf'):
                filename = os.path.basename(link)
            
            filepath = self.download_file(link, filename)
            
            if filepath:
                downloaded_files.append(filepath)
        
        logger.info(f"Downloaded {len(downloaded_files)} files")
        return downloaded_files

def main():
    """Main function to run the downloader"""
    downloader = WHODataDownloader()
    
    try:
        # Download datasets using cached links
        downloaded_files = downloader.download_datasets(use_cached_links=True)
        
        if downloaded_files:
            print("\nDownloaded files:")
            for file in downloaded_files:
                print(f"  - {file}")
        else:
            print("No files were downloaded.")
            
    except KeyboardInterrupt:
        logger.info("Download process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

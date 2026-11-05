import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from who_dataset_downloader import WHODataDownloader
from who_link_crawler import WHOLinkCrawler

def test_link_crawler():
    """Test that the link crawler works correctly"""
    print("Testing link crawler...")
    
    # Create a temporary output file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_file = f.name
    
    try:
        # Mock the session to avoid actual HTTP requests
        with patch('who_link_crawler.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.return_value.content = b'<html><a href="/test.pdf">Test</a></html>'
            mock_session_class.return_value = mock_session
            
            crawler = WHOLinkCrawler(output_file=temp_file)
            
            # Test with a simple URL
            result = crawler.crawl_page("https://www.who.int/test", max_depth=1)
            
            print(f"Link crawler test completed. Found {len(result)} links")
            return True
            
    except Exception as e:
        print(f"Link crawler test failed: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_downloader():
    """Test that the downloader works correctly"""
    print("Testing dataset downloader...")
    
    try:
        # Mock the session to avoid actual HTTP requests
        with patch('who_dataset_downloader.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.return_value.content = b'<html><a href="/test.pdf">Test</a></html>'
            mock_session.get.return_value.status_code = 200
            mock_session_class.return_value = mock_session
            
            # Create a temporary download directory
            with tempfile.TemporaryDirectory() as temp_dir:
                downloader = WHODataDownloader(download_dir=temp_dir)
                
                # Test with a simple URL
                result = downloader.find_pdf_links("https://www.who.int/test")
                
                print(f"Downloader test completed. Found {len(result)} PDF links")
                return True
                
    except Exception as e:
        print(f"Downloader test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running tests for WHO data downloader...")
    
    success = True
    
    # Test the link crawler
    if not test_link_crawler():
        success = False
        
    # Test the downloader
    if not test_downloader():
        success = False
    
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
    
    return success

if __name__ == "__main__":
    main()

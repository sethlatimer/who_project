#!/usr/bin/env python3
"""
Simple test script to verify WHO downloader functionality
without making actual network requests.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_downloader_functionality():
    """Test that the downloader can be instantiated and methods called"""
    
    print("Testing downloader functionality...")
    
    try:
        # Import after adding to path
        from who_dataset_downloader import WHODataDownloader
        
        # Test instantiation
        downloader = WHODataDownloader()
        print("✓ Downloader instantiated successfully")
        
        # Test method existence
        assert hasattr(downloader, 'find_pdf_links')
        assert hasattr(downloader, 'find_dataset_links')
        assert hasattr(downloader, 'download_file')
        assert hasattr(downloader, 'search_who_datasets')
        assert hasattr(downloader, 'download_datasets')
        print("✓ All expected methods exist")
        
        # Test that download directory is created
        assert os.path.exists('who_datasets')
        print("✓ Download directory exists")
        
        print("\nAll basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

def test_crawler_functionality():
    """Test that the crawler can be instantiated"""
    
    print("\nTesting crawler functionality...")
    
    try:
        # Import after adding to path
        from who_link_crawler import WHOLinkCrawler
        
        # Test instantiation
        crawler = WHOLinkCrawler()
        print("✓ Crawler instantiated successfully")
        
        # Test method existence
        assert hasattr(crawler, 'crawl_page')
        assert hasattr(crawler, 'extract_links')
        assert hasattr(crawler, 'save_links')
        print("✓ All expected methods exist")
        
        print("\nAll crawler functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Running simple functionality tests...")
    
    success = True
    success &= test_downloader_functionality()
    success &= test_crawler_functionality()
    
    if success:
        print("\n✓ All tests passed! The scripts are properly structured.")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)

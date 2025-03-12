"""
Test script for the crawler's contact page finding process.
"""

import asyncio
from http_handler import HTTPHandler
from playwright_handler import PlaywrightHandler
from crawler import Crawler
from utils import logger, is_likely_contact_page

async def test_crawler():
    """Test the crawler's contact page finding process."""
    # Initialize HTTP handler
    http_handler = HTTPHandler()
    
    # Initialize Playwright handler
    playwright_handler = PlaywrightHandler()
    await playwright_handler.setup_browser()
    
    try:
        # Initialize crawler
        crawler = Crawler(http_handler, playwright_handler)
        
        # Test URL
        test_url = "http://sportguru.ro"
        
        print(f"Testing contact page finding for: {test_url}")
        print("-" * 80)
        
        # Find contact pages
        contact_pages = await crawler.find_contact_pages(test_url)
        
        print(f"Found {len(contact_pages)} potential contact pages:")
        for i, page in enumerate(contact_pages, 1):
            # Calculate score for each page
            score = is_likely_contact_page(page)
            print(f"{i}. {page} (Score: {score})")
        
        print("-" * 80)
        print("Checking if contact page is prioritized...")
        
        # Check if the contact page is in the top results
        contact_page_found = False
        for i, page in enumerate(contact_pages[:3]):  # Check top 3 results
            if "/contact" in page.lower():
                print(f"SUCCESS: Contact page found at position {i+1}: {page}")
                contact_page_found = True
                break
        
        if not contact_page_found:
            print("FAILURE: Contact page not found in top results")
        
    finally:
        # Clean up resources
        await playwright_handler.cleanup()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_crawler())
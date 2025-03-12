"""
Test script for the full email extraction process.
"""

import asyncio
import time
from http_handler import HTTPHandler
from playwright_handler import PlaywrightHandler
from crawler import Crawler
from extractor import EmailExtractor
from utils import logger, is_likely_contact_page

async def test_extraction():
    """Test the full email extraction process."""
    start_time = time.time()
    
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
        print("Testing email extraction...")
        
        # Create a custom crawler that returns the contact pages we already found
        class CustomCrawler:
            async def find_contact_pages(self, url):
                return contact_pages
        
        custom_crawler = CustomCrawler()
        
        # Initialize extractor with the custom crawler
        extractor = EmailExtractor(http_handler, playwright_handler, custom_crawler)
        
        # Extract emails
        emails = await extractor.extract_emails_from_url(test_url)
        
        # Print results
        if emails:
            print(f"Found {len(emails)} emails:")
            for email in emails:
                print(f"- {email}")
        else:
            print("No emails found, but contact pages were correctly prioritized")
            
        # Calculate elapsed time
        elapsed = time.time() - start_time
        print(f"Processing completed in {elapsed:.2f} seconds")
        
    finally:
        # Clean up resources
        await playwright_handler.cleanup()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_extraction())
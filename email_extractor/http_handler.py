"""
HTTP request handler for the Email Extractor.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urljoin

from config import HTTP_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF_FACTOR
from utils import (
    get_random_user_agent, extract_emails_from_text, 
    normalize_url, is_likely_contact_page, decode_email_entities,
    logger
)

class HTTPHandler:
    """Handles HTTP requests and email extraction from HTML content."""
    
    def __init__(self):
        """Initialize the HTTP handler with a session."""
        self.session = requests.Session()
        self.visited_urls = set()
    
    def _get_headers(self):
        """Get request headers with a random user agent."""
        return {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=RETRY_BACKOFF_FACTOR, min=1, max=10),
        reraise=True
    )
    def fetch_url(self, url):
        """
        Fetch a URL with retry logic.
        
        Args:
            url (str): The URL to fetch
            
        Returns:
            tuple: (response_text, soup) or (None, None) if failed
        """
        if url in self.visited_urls:
            logger.debug(f"Skipping already visited URL: {url}")
            return None, None
        
        self.visited_urls.add(url)
        
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=HTTP_TIMEOUT,
                allow_redirects=True
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                return None, None
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {content_type} for {url}")
                return None, None
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'lxml')
            return response.text, soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise  # Let retry handle this
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            return None, None
    
    def extract_emails_from_page(self, url):
        """
        Extract emails from a web page.
        
        Args:
            url (str): The URL to extract emails from
            
        Returns:
            list: List of extracted email addresses
        """
        html_text, soup = self.fetch_url(url)
        if not html_text or not soup:
            return []
        
        emails = []
        
        # Method 1: Extract from raw HTML (catches obfuscated emails)
        decoded_html = decode_email_entities(html_text)
        raw_emails = extract_emails_from_text(decoded_html)
        emails.extend(raw_emails)
        
        # Method 2: Extract from visible text
        if soup:
            # Get all text from the page
            visible_text = soup.get_text(" ", strip=True)
            text_emails = extract_emails_from_text(visible_text)
            emails.extend(text_emails)
            
            # Method 3: Check mailto links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href[7:]  # Remove 'mailto:'
                    # Handle additional parameters in mailto links
                    if '?' in email:
                        email = email.split('?')[0]
                    if email and email not in emails:
                        emails.append(email)
        
        # Remove duplicates while preserving order
        unique_emails = []
        seen = set()
        for email in emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        
        logger.info(f"Extracted {len(unique_emails)} emails from {url}")
        return unique_emails
    
    def find_contact_pages(self, base_url, soup):
        """
        Find potential contact pages from the given soup.
        
        Args:
            base_url (str): The base URL
            soup (BeautifulSoup): The parsed HTML
            
        Returns:
            list: List of contact page URLs sorted by relevance
        """
        if not soup:
            return []
        
        contact_links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith(('javascript:', '#', 'tel:', 'mailto:')):
                continue
            
            # Normalize the URL
            full_url = normalize_url(href, base_url)
            if not full_url:
                continue
            
            # Calculate contact page likelihood score
            score = is_likely_contact_page(full_url, link_text)
            if score > 0:
                contact_links.append((full_url, score))
        
        # Sort by score (highest first) and remove duplicates
        contact_links.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the URLs, preserving order but removing duplicates
        unique_urls = []
        seen = set()
        for url, _ in contact_links:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Found {len(unique_urls)} potential contact pages")
        return unique_urls
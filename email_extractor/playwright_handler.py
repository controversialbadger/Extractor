"""
Playwright handler for the Email Extractor.
"""

import asyncio
import re
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from config import (
    PLAYWRIGHT_TIMEOUT, HEADLESS, BROWSER_TYPE, 
    SLOW_MO, ACCEPT_COOKIE_KEYWORDS
)
from utils import (
    get_random_user_agent, extract_emails_from_text, 
    normalize_url, is_likely_contact_page, decode_email_entities,
    logger
)

class PlaywrightHandler:
    """Handles browser automation using Playwright."""
    
    def __init__(self):
        """Initialize the Playwright handler."""
        self.browser = None
        self.context = None
        self.page = None
        self.visited_urls = set()
    
    async def __aenter__(self):
        """Set up the browser when entering the context manager."""
        await self.setup_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting the context manager."""
        await self.cleanup()
    
    async def setup_browser(self):
        """Set up the Playwright browser."""
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser type
            if BROWSER_TYPE == "firefox":
                browser_engine = self.playwright.firefox
            elif BROWSER_TYPE == "webkit":
                browser_engine = self.playwright.webkit
            else:
                browser_engine = self.playwright.chromium
            
            # Launch browser
            self.browser = await browser_engine.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO
            )
            
            # Create a context with custom user agent
            self.context = await self.browser.new_context(
                user_agent=get_random_user_agent(),
                viewport={'width': 1280, 'height': 800},
                java_script_enabled=True,
                ignore_https_errors=True
            )
            
            # Set default timeout
            self.context.set_default_timeout(PLAYWRIGHT_TIMEOUT * 1000)  # Convert to ms
            
            # Create a page
            self.page = await self.context.new_page()
            
            # Set up event handlers
            self.page.on("dialog", self._handle_dialog)
            
            logger.info("Playwright browser setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Playwright browser: {str(e)}")
            await self.cleanup()
            return False
    
    async def _handle_dialog(self, dialog):
        """Handle dialogs (alerts, confirms, prompts)."""
        logger.info(f"Dismissing dialog: {dialog.message}")
        await dialog.dismiss()
    
    async def _handle_cookie_banners(self):
        """Attempt to handle cookie consent banners."""
        try:
            # Look for common cookie consent buttons
            for keyword in ACCEPT_COOKIE_KEYWORDS:
                # Try different selector strategies
                selectors = [
                    f"button:has-text('{keyword}')",
                    f"button:has-text('{keyword.upper()}')",
                    f"button:has-text('{keyword.capitalize()}')",
                    f"a:has-text('{keyword}')",
                    f"div:has-text('{keyword}'):visible",
                    f"[id*='cookie'] button",
                    f"[class*='cookie'] button",
                    f"[id*='consent'] button",
                    f"[class*='consent'] button",
                    f"[id*='gdpr'] button",
                    f"[class*='gdpr'] button"
                ]
                
                for selector in selectors:
                    try:
                        button = await self.page.wait_for_selector(selector, timeout=5000)
                        if button:
                            await button.click()
                            logger.info(f"Clicked cookie consent button: {selector}")
                            await self.page.wait_for_timeout(1000)  # Wait for banner to disappear
                            return True
                    except:
                        continue
            
            return False
        except Exception as e:
            logger.warning(f"Error handling cookie banner: {str(e)}")
            return False
    
    async def navigate_to_url(self, url):
        """
        Navigate to a URL using Playwright.
        
        Args:
            url (str): The URL to navigate to
            
        Returns:
            tuple: (success, html_content, soup)
        """
        if url in self.visited_urls:
            logger.debug(f"Skipping already visited URL: {url}")
            return False, None, None
        
        self.visited_urls.add(url)
        
        try:
            # Navigate to the URL
            logger.info(f"Navigating to URL with Playwright: {url}")
            response = await self.page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT * 1000)
            
            if not response:
                logger.warning(f"Failed to navigate to {url}: No response")
                return False, None, None
            
            if not response.ok:
                logger.warning(f"Failed to navigate to {url}, status: {response.status}")
                return False, None, None
            
            # Handle cookie banners
            await self._handle_cookie_banners()
            
            # Wait for the page to be fully loaded
            await self.page.wait_for_load_state("networkidle")
            
            # Get the page content
            html_content = await self.page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            
            return True, html_content, soup
            
        except Exception as e:
            logger.error(f"Error navigating to {url} with Playwright: {str(e)}")
            return False, None, None
    
    async def extract_emails_from_page(self, url):
        """
        Extract emails from a web page using Playwright.
        
        Args:
            url (str): The URL to extract emails from
            
        Returns:
            list: List of extracted email addresses
        """
        success, html_content, soup = await self.navigate_to_url(url)
        if not success or not html_content:
            return []
        
        emails = []
        
        # Method 1: Extract from raw HTML (catches obfuscated emails)
        decoded_html = decode_email_entities(html_content)
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
        
        # Method 4: Execute JavaScript to find emails that might be generated dynamically
        try:
            # Get all text content from the page using JavaScript
            js_text = await self.page.evaluate('''
                () => {
                    return document.body.innerText;
                }
            ''')
            js_emails = extract_emails_from_text(js_text)
            emails.extend(js_emails)
            
            # Look for elements with onclick handlers that might reveal emails
            email_elements = await self.page.query_selector_all('[onclick*="mail"], [onclick*="email"]')
            for element in email_elements:
                try:
                    await element.click()
                    await self.page.wait_for_timeout(500)  # Wait for any changes
                    
                    # Get updated page content
                    updated_html = await self.page.content()
                    updated_soup = BeautifulSoup(updated_html, 'lxml')
                    
                    # Extract emails from the updated content
                    updated_text = updated_soup.get_text(" ", strip=True)
                    updated_emails = extract_emails_from_text(updated_text)
                    emails.extend(updated_emails)
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error executing JavaScript for email extraction: {str(e)}")
        
        # Remove duplicates while preserving order
        unique_emails = []
        seen = set()
        for email in emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        
        logger.info(f"Extracted {len(unique_emails)} emails from {url} using Playwright")
        return unique_emails
    
    async def find_contact_pages(self, base_url):
        """
        Find potential contact pages from the current page.
        
        Args:
            base_url (str): The base URL
            
        Returns:
            list: List of contact page URLs sorted by relevance
        """
        try:
            # Get all links from the page
            links = await self.page.query_selector_all('a[href]')
            
            contact_links = []
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    link_text = await link.text_content()
                    
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
                except:
                    continue
            
            # Sort by score (highest first) and remove duplicates
            contact_links.sort(key=lambda x: x[1], reverse=True)
            
            # Extract just the URLs, preserving order but removing duplicates
            unique_urls = []
            seen = set()
            for url, _ in contact_links:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            logger.info(f"Found {len(unique_urls)} potential contact pages using Playwright")
            return unique_urls
            
        except Exception as e:
            logger.error(f"Error finding contact pages with Playwright: {str(e)}")
            return []
    
    async def cleanup(self):
        """Clean up Playwright resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("Playwright resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Playwright resources: {str(e)}")
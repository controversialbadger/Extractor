"""
Configuration settings for the Email Extractor.
"""

# Timeout settings (in seconds)
HTTP_TIMEOUT = 15  # Reduced from 30
PLAYWRIGHT_TIMEOUT = 20  # Reduced from 60
GLOBAL_TIMEOUT = 120  # Reduced from 300 (2 minutes max per website)
COOKIE_BANNER_TIMEOUT = 3  # Timeout for cookie banner handling
PAGE_NAVIGATION_TIMEOUT = 15  # Timeout for page navigation
CONTACT_PAGE_SEARCH_TIMEOUT = 30  # Increased from 10 to 30 seconds

# Retry settings
MAX_RETRIES = 2  # Reduced from 3
RETRY_BACKOFF_FACTOR = 1  # Reduced from 2

# Crawler settings
MAX_CONTACT_PAGES = 3  # Reduced from 5
MAX_DEPTH = 2  # Reduced from 3
MAX_PAGES_PER_DOMAIN = 10  # Reduced from 20

# User-Agent settings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
]

# Playwright settings
HEADLESS = True
BROWSER_TYPE = "chromium"  # Options: chromium, firefox, webkit
SLOW_MO = 10  # Reduced from 50ms

# Output settings
OUTPUT_FILE = "output.txt"

# Anti-bot settings
COOKIES_ENABLED = True
ACCEPT_COOKIE_KEYWORDS = [
    "accept", "accept all", "agree", "ok", "got it", "i understand", 
    "akzeptieren", "accepter", "aceptar", "aceitar", "accetto"
]
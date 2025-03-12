"""
Utility functions for the Email Extractor.
"""

import re
import logging
import random
import tldextract
from urllib.parse import urljoin, urlparse
from config import USER_AGENTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_extractor')

# Email regex pattern - comprehensive pattern to catch various email formats
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Contact page keywords in multiple languages
CONTACT_KEYWORDS = {
    # English
    'en': ['contact', 'about', 'about us', 'about-us', 'team', 'imprint', 'impressum', 'legal', 'privacy'],
    # German
    'de': ['kontakt', 'über uns', 'ueber uns', 'impressum', 'team', 'datenschutz'],
    # French
    'fr': ['contact', 'à propos', 'a propos', 'équipe', 'equipe', 'mentions légales', 'mentions legales'],
    # Spanish
    'es': ['contacto', 'acerca', 'sobre nosotros', 'equipo', 'aviso legal'],
    # Italian
    'it': ['contatto', 'contatti', 'chi siamo', 'team', 'note legali'],
    # Dutch
    'nl': ['contact', 'over ons', 'team', 'juridisch'],
    # Polish
    'pl': ['kontakt', 'o nas', 'zespół', 'zespol', 'informacje prawne'],
    # Swedish
    'sv': ['kontakt', 'om oss', 'team', 'juridisk information'],
    # Danish
    'da': ['kontakt', 'om os', 'team', 'juridisk information'],
    # Finnish
    'fi': ['yhteystiedot', 'meistä', 'meista', 'tiimi', 'oikeudelliset tiedot'],
    # Greek
    'el': ['επικοινωνία', 'σχετικά με', 'ομάδα', 'νομικές πληροφορίες'],
    # Portuguese
    'pt': ['contato', 'contacto', 'sobre nós', 'sobre nos', 'equipe', 'equipa', 'informações legais', 'informacoes legais'],
    # Czech
    'cs': ['kontakt', 'o nás', 'o nas', 'tým', 'tym', 'právní informace', 'pravni informace'],
    # Hungarian
    'hu': ['kapcsolat', 'rólunk', 'rolunk', 'csapat', 'jogi információk', 'jogi informaciok'],
    # Romanian
    'ro': ['contact', 'despre noi', 'echipă', 'echipa', 'informații legale', 'informatii legale'],
    # Bulgarian
    'bg': ['контакт', 'за нас', 'екип', 'правна информация'],
    # Croatian
    'hr': ['kontakt', 'o nama', 'tim', 'pravne informacije'],
    # Estonian
    'et': ['kontakt', 'meist', 'meeskond', 'õiguslik teave', 'oiguslik teave'],
    # Latvian
    'lv': ['kontakti', 'par mums', 'komanda', 'juridiskā informācija', 'juridiska informacija'],
    # Lithuanian
    'lt': ['kontaktai', 'apie mus', 'komanda', 'teisinė informacija', 'teisine informacija'],
    # Slovenian
    'sl': ['kontakt', 'o nas', 'ekipa', 'pravne informacije'],
    # Slovak
    'sk': ['kontakt', 'o nás', 'o nas', 'tím', 'tim', 'právne informácie', 'pravne informacie'],
    # Maltese
    'mt': ['kuntatt', 'dwar', 'tim', 'informazzjoni legali'],
    # Irish
    'ga': ['teagmháil', 'teagmhail', 'fúinn', 'fuinn', 'foireann', 'eolas dlíthiúil', 'eolas dlithiuil'],
}

# We no longer need to flatten contact keywords since our new approach is language-agnostic
# and doesn't rely on hardcoded terms

def get_random_user_agent():
    """Return a random user agent from the configured list."""
    return random.choice(USER_AGENTS)

def is_valid_url(url):
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url, base_url=None):
    """Normalize a URL by handling relative paths and removing fragments."""
    if not url:
        return None
    
    # Handle relative URLs
    if base_url and not urlparse(url).netloc:
        url = urljoin(base_url, url)
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Reconstruct the URL without fragments
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized

def get_domain(url):
    """Extract the domain from a URL."""
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"

def is_same_domain(url1, url2):
    """Check if two URLs belong to the same domain."""
    return get_domain(url1) == get_domain(url2)

def get_contact_page_patterns():
    """
    Intelligently generate contact page patterns without hardcoded paths.
    Uses structural analysis of common URL patterns across languages.
    
    Returns a tuple of (structural_patterns, position_indicators, common_url_segments)
    """
    # Structural patterns based on URL path analysis
    structural_patterns = [
        # Common URL structure patterns (language-agnostic)
        r'/[^/]{3,15}/?$',  # Short single-word paths at the end of URL
        r'/[^/]{3,15}/form/?$',  # Contact form pages
        r'/[^/]{3,15}-[^/]{2,10}/?$',  # Hyphenated paths (like contact-us)
        r'/[^/]{3,15}_[^/]{2,10}/?$',  # Underscore paths (like contact_us)
        r'/[a-z]{2}/[^/]{3,15}/?$',  # Language prefix followed by short path
    ]
    
    # Position indicators - common positions in site hierarchy
    position_indicators = [
        r'^https?://[^/]+/[^/]+/?$',  # Top-level pages
        r'^https?://[^/]+/[a-z]{2}/[^/]+/?$',  # Top-level with language code
    ]
    
    # Common URL segments that might indicate contact pages (structural, not linguistic)
    common_url_segments = [
        '/c/',  # Abbreviated paths
        '/info/',
        '/support/',
        '/help/',
        '/reach/',
        '/connect/',
        '/get-in-touch/',
        '/write-to-us/',
        '/feedback/',
    ]
    
    return structural_patterns, position_indicators, common_url_segments

def is_likely_contact_page(url, link_text=None):
    """
    Intelligently determine if a URL is likely to be a contact page using structural analysis.
    This approach doesn't rely on hardcoded language-specific terms.
    
    Returns a score from 0-10 indicating likelihood (10 being highest).
    """
    score = 0
    url_lower = url.lower()
    
    # 1. URL Structure Analysis
    
    # Check for short paths at the end of the URL (typical of contact pages)
    path = urlparse(url_lower).path
    path_segments = [s for s in path.split('/') if s]
    
    # Contact pages often have short paths with few segments
    if len(path_segments) == 1 and 3 <= len(path_segments[0]) <= 15:
        score += 3
    elif len(path_segments) == 1 and len(path_segments[0]) <= 2:  # Ultra-abbreviated paths like /c or /i
        score += 4  # Give higher score to ultra-abbreviated paths
    
    # Contact pages are often at the top level of the site
    if len(path_segments) <= 2:
        score += 2
    
    # Get structural patterns
    structural_patterns, position_indicators, common_url_segments = get_contact_page_patterns()
    
    # Check structural patterns
    for pattern in structural_patterns:
        if re.search(pattern, url_lower):
            score += 3
            break
    
    # Check position in site hierarchy
    for pattern in position_indicators:
        if re.search(pattern, url_lower):
            score += 2
            break
    
    # Check common URL segments
    for segment in common_url_segments:
        if segment in url_lower:
            score += 2
            break
    
    # Special case for ultra-abbreviated paths like /c/f (contact form)
    if re.search(r'^/[a-z]/[a-z]/?$', path):
        score += 3
    
    # 2. Link Text Analysis (if provided)
    if link_text:
        link_text_lower = link_text.lower()
        
        # Short link texts are common for contact pages
        if len(link_text_lower) <= 15:
            score += 1
        
        # Check for common structural patterns in link text
        if re.search(r'^[^\s]{3,15}$', link_text_lower):  # Single short word
            score += 2
        
        if re.search(r'^[^\s]{3,10}\s[^\s]{2,5}$', link_text_lower):  # Two short words
            score += 2
        
        # Check for icons or symbols often used with contact links
        if '@' in link_text or '✉' in link_text or '📧' in link_text or '📞' in link_text:
            score += 3
            
        # Check for contact-related terms in link text (language-agnostic approach)
        contact_indicators = ['contact', 'email', 'mail', 'message', 'send', 'write', 
                             'touch', 'reach', 'connect', 'feedback', 'help', 'support',
                             'info', 'information', 'form']  # Added info, information, form
        for indicator in contact_indicators:
            if indicator in link_text_lower:
                score += 2
                break
    
    # 3. TLD and Domain Analysis
    
    # Check if the domain suggests a specific country/language
    tld = urlparse(url_lower).netloc.split('.')[-1]
    if tld in ['de', 'fr', 'es', 'it', 'nl', 'pl', 'se', 'dk', 'fi', 'gr', 'pt', 'cz', 'hu', 'ro', 'bg', 'hr', 'ee', 'lv', 'lt', 'si', 'sk', 'mt', 'ie']:
        # For country-specific domains, we can infer they're more likely to be important pages
        if len(path_segments) <= 2:
            score += 1
    
    # 4. Penalize patterns unlikely to be contact pages
    
    # Penalize very long URLs (likely not contact pages)
    if len(url) > 100:
        score -= 2
    
    # Penalize URLs with many query parameters
    if '?' in url and len(url.split('?')[1]) > 20:
        score -= 1
    
    # Penalize URLs that look like product or category pages
    product_indicators = [
        r'/product', r'/category', r'/shop', r'/store', r'/item', r'/catalog',
        r'/collection', r'/gallery', r'/portfolio', r'/blog', r'/news', r'/article',
        r'/p/', r'/download', r'/media', r'/image', r'/video',  # Removed /c/ and /i/ as they can be abbreviations
        r'/tag/', r'/search', r'/filter', r'/sort', r'/list', r'/view', r'/cart',
        r'/checkout', r'/payment', r'/order', r'/shipping', r'/delivery',
        r'/\d{4}/', r'/\d{2}-\d{2}-\d{4}/'  # Date patterns
    ]
    
    for pattern in product_indicators:
        if re.search(pattern, url_lower):
            score -= 3
            break
    
    # 5. Contextual boosting
    
    # Boost URLs with email-related segments
    if 'mail' in url_lower or 'email' in url_lower or 'message' in url_lower:
        score += 2
    
    # Boost URLs with form-related segments
    if 'form' in url_lower or 'send' in url_lower or 'submit' in url_lower:
        score += 1
    
    # Boost URLs with info-related segments
    if 'info' in url_lower or 'information' in url_lower:
        score += 1
    
    # Ensure score is between 0 and 10
    return min(max(score, 0), 10)

def extract_emails_from_text(text):
    """Extract email addresses from text using regex."""
    if not text:
        return []
    
    # Find all email matches
    emails = re.findall(EMAIL_REGEX, text)
    
    # Normalize and deduplicate
    normalized_emails = []
    seen = set()
    
    for email in emails:
        email = email.lower().strip()
        if email not in seen and is_valid_email(email):
            seen.add(email)
            normalized_emails.append(email)
    
    return normalized_emails

def is_valid_email(email):
    """Validate an email address."""
    # Basic validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    
    # Check for common invalid patterns
    invalid_patterns = [
        r'@example\.com$',
        r'@sample\.com$',
        r'@domain\.com$',
        r'@email\.com$',
        r'@test\.com$',
        r'@yourcompany\.com$',
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, email, re.IGNORECASE):
            return False
    
    return True

def decode_email_entities(text):
    """Decode HTML entities in email addresses."""
    # Common HTML entity replacements
    entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&#64;': '@',
        '&#46;': '.',
        '&#45;': '-',
        '&#95;': '_',
        '&period;': '.',
        '&commat;': '@',
        '&hyphen;': '-',
        '&lowbar;': '_',
    }
    
    # Replace entities
    for entity, char in entities.items():
        text = text.replace(entity, char)
    
    # Handle numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    
    return text
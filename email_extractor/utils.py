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

# Flatten the contact keywords for easier searching
ALL_CONTACT_KEYWORDS = set()
for lang_keywords in CONTACT_KEYWORDS.values():
    ALL_CONTACT_KEYWORDS.update(lang_keywords)

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

def is_likely_contact_page(url, link_text=None):
    """
    Determine if a URL is likely to be a contact page based on its URL and link text.
    Returns a score from 0-10 indicating likelihood (10 being highest).
    """
    score = 0
    url_lower = url.lower()
    
    # Check URL path for contact keywords
    for keyword in ALL_CONTACT_KEYWORDS:
        keyword_lower = keyword.lower()
        # Exact match in path gets higher score
        if f"/{keyword_lower}" in url_lower or f"/{keyword_lower}/" in url_lower:
            score += 7
            break
        # Partial match in URL
        elif keyword_lower in url_lower:
            score += 5
            break
    
    # If link text is provided, check it for contact keywords
    if link_text:
        link_text_lower = link_text.lower()
        for keyword in ALL_CONTACT_KEYWORDS:
            keyword_lower = keyword.lower()
            # Exact match in link text gets higher score
            if link_text_lower == keyword_lower:
                score += 8
                break
            # Partial match in link text
            elif keyword_lower in link_text_lower:
                score += 5
                break
    
    # Check for common contact page patterns in URL
    contact_patterns = [
        r'/contact', r'/kontakt', r'/contacto', r'/contatti', r'/contact-us',
        r'/about', r'/about-us', r'/ueber-uns', r'/impressum', r'/imprint',
        r'/get-in-touch', r'/reach-us', r'/reach-out', r'/connect'
    ]
    
    for pattern in contact_patterns:
        if re.search(pattern, url_lower):
            score += 3
            break
    
    # Boost score for URLs with 'contact' or equivalent in the path
    if '/contact' in url_lower or '/kontakt' in url_lower:
        score += 2
    
    # Penalize very long URLs (likely not contact pages)
    if len(url) > 100:
        score -= 2
    
    return min(score, 10)  # Cap at 10

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
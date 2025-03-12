"""
Test script for contact page detection logic.
"""

import re
from utils import is_likely_contact_page, get_contact_page_patterns

def test_contact_page_detection():
    """Test the contact page detection logic with various URLs."""
    test_cases = [
        # URL, Link Text, Expected High Score (>7)
        # English
        ("https://www.example.com/contact", "Contact", True),
        ("https://www.example.com/contact-us", "Contact Us", True),
        ("https://www.example.com/about", "About Us", True),
        ("https://www.example.com/about-us", "About", True),
        
        # German
        ("https://www.example.de/kontakt", "Kontakt", True),
        ("https://www.example.de/ueber-uns", "Über uns", True),
        ("https://www.example.de/impressum", "Impressum", True),
        
        # French
        ("https://www.example.fr/contact", "Contact", True),
        ("https://www.example.fr/contactez-nous", "Contactez-nous", True),
        ("https://www.example.fr/a-propos", "À propos", True),
        
        # Spanish
        ("https://www.example.es/contacto", "Contacto", True),
        ("https://www.example.es/sobre-nosotros", "Sobre nosotros", True),
        
        # Italian
        ("https://www.example.it/contatti", "Contatti", True),
        ("https://www.example.it/chi-siamo", "Chi siamo", True),
        
        # Dutch
        ("https://www.example.nl/contact", "Contact", True),
        ("https://www.example.nl/over-ons", "Over ons", True),
        
        # Polish
        ("https://www.example.pl/kontakt", "Kontakt", True),
        ("https://www.example.pl/o-nas", "O nas", True),
        
        # Swedish
        ("https://www.example.se/kontakt", "Kontakt", True),
        ("https://www.example.se/om-oss", "Om oss", True),
        
        # Finnish
        ("https://www.example.fi/yhteystiedot", "Yhteystiedot", True),
        ("https://www.example.fi/meista", "Meistä", True),
        
        # Greek
        ("https://www.example.gr/epikoinonia", "Επικοινωνία", True),
        ("https://www.example.gr/sxetika-me", "Σχετικά με", True),
        
        # Portuguese
        ("https://www.example.pt/contacto", "Contacto", True),
        ("https://www.example.pt/sobre-nos", "Sobre nós", True),
        
        # Hungarian
        ("https://www.example.hu/kapcsolat", "Kapcsolat", True),
        ("https://www.example.hu/rolunk", "Rólunk", True),
        
        # Romanian
        ("https://www.example.ro/contact", "Contact", True),
        ("https://www.example.ro/despre-noi", "Despre noi", True),
        ("https://www.example.ro/contacte", "Contacte", True),
        
        # Product/category pages that should get low scores
        ("https://www.example.com/products/category/items", "Products", False),
        ("https://www.example.com/shop/category/subcategory", "Shop", False),
        ("https://www.example.com/store/items/product", "Store", False),
        
        # Edge cases
        ("https://www.example.com/contact/form", "Contact Form", True),
        ("https://www.example.com/about/team", "Our Team", True),
        ("https://www.example.com/blog/contact-info", "Contact Information", True),
        ("https://www.example.com/en/contact", "Contact", True),  # With language prefix
        ("https://www.example.com/de/kontakt", "Kontakt", True),  # With language prefix
    ]
    
    print("Testing contact page detection logic...")
    print("-" * 80)
    print(f"{'URL':<50} | {'Link Text':<20} | {'Score':<5} | {'Expected':<8} | {'Result'}")
    print("-" * 80)
    
    for url, link_text, expected_high_score in test_cases:
        score = is_likely_contact_page(url, link_text)
        is_high_score = score > 7
        result = "PASS" if is_high_score == expected_high_score else "FAIL"
        
        print(f"{url:<50} | {link_text:<20} | {score:<5} | {expected_high_score!s:<8} | {result}")
    
    print("-" * 80)

def test_pattern_generation():
    """Test the dynamic pattern generation."""
    exact_patterns, partial_patterns, contact_terms = get_contact_page_patterns()
    
    print("\nTesting pattern generation...")
    print("-" * 80)
    print(f"Generated {len(exact_patterns)} exact patterns")
    print(f"Generated {len(partial_patterns)} partial patterns")
    print(f"Generated {len(contact_terms)} contact terms")
    
    # Print a sample of each
    print("\nSample exact patterns:")
    for pattern in list(exact_patterns)[:5]:
        print(f"- {pattern}")
    
    print("\nSample partial patterns:")
    for pattern in list(partial_patterns)[:5]:
        print(f"- {pattern}")
    
    print("\nSample contact terms:")
    for term in list(contact_terms)[:5]:
        print(f"- {term}")
    
    print("-" * 80)

if __name__ == "__main__":
    test_contact_page_detection()
    test_pattern_generation()
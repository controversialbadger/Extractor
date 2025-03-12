"""
Test script for contact page detection logic.
"""

import re
from utils import is_likely_contact_page

def test_contact_page_detection():
    """Test the contact page detection logic with various URLs."""
    test_cases = [
        # URL, Link Text, Expected High Score (>7)
        ("https://www.sportguru.ro/contact", "Contact", True),
        ("https://www.sportguru.ro/contacte", "Contacte", True),
        ("https://www.sportguru.ro/about", "About Us", True),
        ("https://www.sportguru.ro/about-us", "About", True),
        ("https://www.sportguru.ro/kontakt", "Kontakt", True),
        ("https://www.sportguru.ro/contacto", "Contacto", True),
        ("https://www.sportguru.ro/impressum", "Impressum", True),
        # Product/category pages that should get low scores
        ("https://www.sportguru.ro/sporturi/alergare/echipament-alergare", "Running Equipment", False),
        ("https://www.sportguru.ro/sporturi/schi/echipament-schi", "Ski Equipment", False),
        ("https://www.sportguru.ro/sporturi/outdoor/echipament-outdoor", "Outdoor Equipment", False),
        ("https://www.sportguru.ro/products/category/items", "Products", False),
        # Edge cases
        ("https://www.sportguru.ro/contact-us/form", "Contact Form", True),
        ("https://www.sportguru.ro/about/team", "Our Team", True),
        ("https://www.sportguru.ro/blog/contact-info", "Contact Information", True),
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

if __name__ == "__main__":
    test_contact_page_detection()
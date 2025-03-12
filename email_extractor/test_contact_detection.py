"""
Test script for contact page detection logic.
"""

import re
from utils import is_likely_contact_page, get_contact_page_patterns

def test_contact_page_detection():
    """Test the contact page detection logic with various URLs."""
    test_cases = [
        # URL, Link Text, Expected High Score (>7)
        # Common patterns across languages
        ("https://www.example.com/contact", "Contact", True),
        ("https://www.example.com/contact-us", "Contact Us", True),
        ("https://www.example.com/about", "About Us", True),
        ("https://www.example.com/about-us", "About", True),
        ("https://www.example.com/c", "Contact", True),  # Abbreviated form
        ("https://www.example.com/i", "Info", True),  # Abbreviated form
        
        # Language-specific examples (testing structural detection, not hardcoded terms)
        ("https://www.example.de/kontakt", "Kontakt", True),
        ("https://www.example.fr/contact", "Contact", True),
        ("https://www.example.es/contacto", "Contacto", True),
        ("https://www.example.it/contatti", "Contatti", True),
        
        # Testing URL structure patterns
        ("https://www.example.com/get-in-touch", "Get in Touch", True),
        ("https://www.example.com/reach-us", "Reach Us", True),
        ("https://www.example.com/feedback", "Feedback", True),
        ("https://www.example.com/help", "Help", True),
        ("https://www.example.com/support", "Support", True),
        
        # Testing with language prefixes
        ("https://www.example.com/en/contact", "Contact", True),
        ("https://www.example.com/de/kontakt", "Kontakt", True),
        ("https://www.example.com/fr/contact", "Contact", True),
        
        # Testing with email-related content
        ("https://www.example.com/email-us", "Email Us", True),
        ("https://www.example.com/send-message", "Send Message", True),
        ("https://www.example.com/write-to-us", "Write to Us", True),
        
        # Product/category pages that should get low scores
        ("https://www.example.com/products/category/items", "Products", False),
        ("https://www.example.com/shop/category/subcategory", "Shop", False),
        ("https://www.example.com/store/items/product", "Store", False),
        ("https://www.example.com/blog/2023/01/article", "Blog Post", False),
        ("https://www.example.com/gallery/images", "Gallery", False),
        
        # Edge cases
        ("https://www.example.com/contact/form", "Contact Form", True),
        ("https://www.example.com/about/team", "Our Team", True),
        ("https://www.example.com/info/contact", "Contact Information", True),
        ("https://www.example.com/c/f", "Contact Form", True),  # Ultra-abbreviated
        ("https://www.example.com/very-long-url-that-is-unlikely-to-be-a-contact-page", "Long URL", False),
        ("https://www.example.com/contact?param1=value1&param2=value2&param3=value3", "Contact with Params", True),
    ]
    
    print("Testing intelligent contact page detection logic...")
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
    """Test the intelligent pattern generation."""
    structural_patterns, position_indicators, common_url_segments = get_contact_page_patterns()
    
    print("\nTesting intelligent pattern generation...")
    print("-" * 80)
    print(f"Generated {len(structural_patterns)} structural patterns")
    print(f"Generated {len(position_indicators)} position indicators")
    print(f"Generated {len(common_url_segments)} common URL segments")
    
    # Print a sample of each
    print("\nSample structural patterns:")
    for pattern in structural_patterns[:5]:
        print(f"- {pattern}")
    
    print("\nSample position indicators:")
    for indicator in position_indicators[:5]:
        print(f"- {indicator}")
    
    print("\nSample common URL segments:")
    for segment in common_url_segments[:5]:
        print(f"- {segment}")
    
    print("-" * 80)

if __name__ == "__main__":
    test_contact_page_detection()
    test_pattern_generation()
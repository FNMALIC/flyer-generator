import os

DEFAULT_CONFIG = {
    # Layout & Sizing
    "flyer_width": 1200,
    "flyer_height": 1600,
    "template_id": "codees_minimal", # "modern_corporate", "marketing_agency", "social_post", "zenith_modern", "codees_minimal", "codees_hero"
    "logo_path": "logo/image.png",
    "image_ratio": 0.55,
    "padding": 80,
    "section_spacing": 50,
    
    # Background & Effects
    "bg_color": "#FDFDFD",
    "primary_color": "#0076BC",  # Codees Blue
    "secondary_color": "#111111",
    "accent_color": "#ED1C24",   # Codees Red
    "shadow_enabled": True,
    "accents_enabled": True,
    
    # Typography Defaults
    "default_font": "DejaVuSans",
    "line_height": 1.4,
    
    "company_font_size": 42,
    "company_font_color": "#2C3E50",
    
    "headline_font_size": 85,
    "headline_font_color": "#2C3E50",
    
    "body_font_size": 28,
    "body_font_color": "#34495E",
    
    "contact_font_size": 24,
    "contact_font_color": "#7F8C8D",
    
    # Defaults for specific sections
    "tagline": "ELEVATING YOUR VISION",
    "cta_text": "WWW.AGENCY-DOMAIN.COM",
    "headline": "MODERN SOLUTIONS FOR YOUR BUSINESS",
    "features": [
        {"title": "INNOVATION", "text": "Driving forward with cutting-edge technology and creative strategies."},
        {"title": "STRATEGY", "text": "Tailored approaches designed to maximize your market impact."},
        {"title": "RESULTS", "text": "Measuring success through tangible growth and performance metrics."}
    ]
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

import os

DEFAULT_CONFIG = {
    # Layout & Sizing
    "flyer_width": 1200,
    "flyer_height": 1600,
    "template_id": "zenith_modern", # Switched from codees_minimal for a more premium default look
    "logo_path": "logo/image.png",
    "image_ratio": 0.55,
    "padding": 80,
    "section_spacing": 60,
    
    # Background & Effects
    "bg_color": "#0D1B2A",       # Deep navy for more premium feel
    "primary_color": "#0076BC",  # Codees Blue
    "secondary_color": "#FFFFFF", # Default to white text on dark bg
    "accent_color": "#ED1C24",   # Codees Red
    "shadow_enabled": True,
    "accents_enabled": True,
    
    # Typography Defaults
    "default_font": "DejaVuSans",
    "line_height": 1.4,
    
    "company_font_size": 48,
    "company_font_color": "#FFFFFF",
    
    "headline_font_size": 85,
    "headline_font_color": "#FFFFFF",
    
    "body_font_size": 28,
    "body_font_color": "#E0E0E0",
    
    "contact_font_size": 24,
    "contact_font_color": "#BBBBBB",
    
    # Defaults for specific sections
    "tagline": "ELEVATING YOUR VISION",
    "cta_text": "WWW.CODEES-CM.COM",
    "headline": "MODERN SOLUTIONS FOR YOUR BUSINESS",
    "features": [
        {"title": "INNOVATION", "text": "Driving forward with cutting-edge technology and creative strategies."},
        {"title": "STRATEGY", "text": "Tailored approaches designed to maximize your market impact."},
        {"title": "RESULTS", "text": "Measuring success through tangible growth and performance metrics."}
    ]
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

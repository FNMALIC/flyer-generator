"""
Regenerate one sample flyer per template_id into samples/ (gitignored).

Run this after changing flyer_generator.py to see what today's code actually
produces, instead of trusting hand-saved PNGs that silently go stale as the
renderers change (which is exactly what happened to the old committed
test_codees_hero.png / local_verified_marketing_v2.png samples this replaces).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from flyer_generator import generate_flyer

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")

SAMPLES = {
    "marketing_agency": {"template": "template_1", "headline": "Modern Solutions", "tagline": "Excellence in every detail", "body_text": "We help you scale fast."},
    "social_post": {"template": "template_2", "headline": "Be Inspired", "body_text": "Great things happen when great people work together."},
    "zenith_modern": {"template": "template_3", "headline": "Elevating Standards", "tagline": "Premium tech consulting", "body_text": "Real growth through real results."},
    "codees_minimal": {"template": "template_4", "headline": "Build The Future", "tagline": "Join our community"},
    "codees_hero": {"template": "logo", "headline": "Digital Transformation", "tagline": "Success stories from Africa"},
    "abstract_business": {"template_id": "abstract_business", "headline": "Codees\nCompany", "tagline": "Empowering Africa's Builders"},
    "abstract_social": {"template_id": "abstract_social", "headline": "Join Codees", "tagline": "Cameroon's Premier Tech Community"},
    "modern_corporate": {"template_id": "modern_corporate", "headline": "Premium Services", "tagline": "Excellence in every detail"},
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, params in SAMPLES.items():
        img = generate_flyer(params)
        path = os.path.join(OUT_DIR, f"{name}.png")
        with open(path, "wb") as f:
            f.write(img.read())
        print(f"wrote {path}")


if __name__ == "__main__":
    main()

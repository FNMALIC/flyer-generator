from flyer_generator import generate_flyer
import os

def test_templates():
    base_params = {
        "image_path": "image.png",
        "company_name": "ANTIGRAVITY",
        "tagline": "ELEVATING INTELLIGENCE",
        "headline": "MINIMAL\nSOPHISTICATION",
        "body_text": "Experience the next level of design with our minimalist execution and glassmorphism effects.",
        "cta_text": "WWW.CORE-ZENITH.AI",
        "features": [
            {"title": "Glassmorphism", "text": "Premium semi-transparent effects."},
            {"title": "Minimalist", "text": "Clean and focused layouts."},
            {"title": "Swiss-Style", "text": "Bold typography and hierarchy."}
        ]
    }

    # Test 1: Zenith Modern (Glassmorphism)
    print("Generating Zenith Modern...")
    p1 = base_params.copy()
    p1["template_id"] = "zenith_modern"
    p1["primary_color"] = "#E67E22"
    with open("test_zenith.png", "wb") as f:
        f.write(generate_flyer(p1).read())

    # Test 2: Elite Corporate (Minimalist White)
    print("Generating Elite Corporate...")
    p2 = base_params.copy()
    p2["template_id"] = "modern_corporate"
    p2["primary_color"] = "#2980B9"
    with open("test_elite.png", "wb") as f:
        f.write(generate_flyer(p2).read())

    # Test 3: Bold Minimalist (Agency style)
    print("Generating Bold Minimalist...")
    p3 = base_params.copy()
    p3["template_id"] = "marketing_agency"
    p3["primary_color"] = "#F1C40F"
    p3["headline"] = "STAY\nBOLD."
    with open("test_bold.png", "wb") as f:
        f.write(generate_flyer(p3).read())

    # Test 4: Social Post
    print("Generating Social Post...")
    p4 = base_params.copy()
    p4["template_id"] = "social_post"
    with open("test_social.png", "wb") as f:
        f.write(generate_flyer(p4).read())

    # Test 5: Codees Minimal
    print("Generating Codees Minimal...")
    p5 = base_params.copy()
    p5["template_id"] = "codees_minimal"
    p5["headline"] = "The Hidden Crisis Behind Cameroon's Hustle Culture"
    p5["tagline"] = "Mental health among entrepreneurs is the silent threat no one's talking about."
    with open("test_codees_minimal.png", "wb") as f:
        f.write(generate_flyer(p5).read())

    # Test 6: Codees Hero
    print("Generating Codees Hero...")
    p6 = base_params.copy()
    p6["template_id"] = "codees_hero"
    p6["headline"] = "Digital Transformation in Traditional Industries"
    p6["tagline"] = "Success Stories From Africa"
    with open("test_codees_hero.png", "wb") as f:
        f.write(generate_flyer(p6).read())

if __name__ == "__main__":
    if not os.path.exists("image.png"):
        print("Error: image.png not found. Please ensure it exists in the root directory.")
    else:
        test_templates()

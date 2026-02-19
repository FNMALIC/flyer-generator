import os
import io
import json
from flyer_generator import generate_flyer

def generate_campaign():
    if not os.path.exists("campaign"):
        os.makedirs("campaign")
    
    campaign_data = [
        {
            "id": "1_brand_awareness",
            "params": {
                "template_id": "codees_minimal",
                "headline": "The Heart of Tech in Cameroon",
                "tagline": "Fostering innovation and collaboration across Africa's tech ecosystem.",
                "cta_text": "www.codees-cm.com"
            }
        },
        {
            "id": "2_mentorship",
            "params": {
                "template_id": "codees_hero",
                "headline": "Scale Your Career With Expert Mentors",
                "tagline": "1:1 Guidance · Industry Leaders · Real Growth",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com"
            }
        },
        {
            "id": "3_incubation",
            "params": {
                "template_id": "codees_minimal",
                "headline": "From Idea to MVP — We Back You",
                "tagline": "Join Cameroon's premier startup incubation program.",
                "cta_text": "JOIN THE HUB"
            }
        },
        {
            "id": "4_hackathon",
            "params": {
                "template_id": "codees_hero",
                "headline": "Code. Create. Conquer.",
                "tagline": "Annual Hackathon · Teams · Prizes",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com"
            }
        },
        {
            "id": "5_workshops",
            "params": {
                "template_id": "zenith_modern",
                "headline": "Level Up Your Tech Skills",
                "tagline": "Expert-led workshops. Every week.",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com",
                "features": [
                    {"title": "Live Q&A with Experts"},
                    {"title": "Hands-On Projects"},
                    {"title": "Community Certificate"}
                ]
            }
        },
        {
            "id": "6_entrepreneurship",
            "params": {
                "template_id": "codees_minimal",
                "headline": "Build Your Startup in Cameroon",
                "tagline": "Join a network of founders, engineers & investors.",
                "cta_text": "CONNECT NOW"
            }
        },
        {
            "id": "7_mentors_recruitment",
            "params": {
                "template_id": "codees_hero",
                "headline": "Become a Codees Mentor",
                "tagline": "Share Expertise · Grow Leaders · Shape Africa's Tech Future",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com"
            }
        },
        {
            "id": "8_funding",
            "params": {
                "template_id": "zenith_modern",
                "headline": "Access Startup Funding in Africa",
                "tagline": "We connect bold ideas with the capital they deserve.",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com",
                "features": [
                    {"title": "Angel Investor Network"},
                    {"title": "Pitch Training & Coaching"},
                    {"title": "Grant & Funding Access"}
                ]
            }
        },
        {
            "id": "9_projects",
            "params": {
                "template_id": "codees_minimal",
                "headline": "Building Cameroon's Digital Future, Together",
                "tagline": "Open-source projects powered by the Codees community.",
                "cta_text": "EXPLORE PROJECTS"
            }
        },
        {
            "id": "10_impact",
            "params": {
                "template_id": "codees_hero",
                "headline": "Real Impact. Real Stories.",
                "tagline": "Success · Innovation · Community",
                "image_path": "image.png",
                "cta_text": "www.codees-cm.com"
            }
        }
    ]

    api_bodies = {}

    for item in campaign_data:
        print(f"Generating flyer: {item['id']}...")
        img_data = generate_flyer(item['params'])
        filename = f"campaign/codees_{item['id']}.png"
        with open(filename, "wb") as f:
            f.write(img_data.read())
        api_bodies[item['id']] = item['params']
    
    with open("campaign_api_bodies.json", "w") as f:
        json.dump(api_bodies, f, indent=4)
    
    print("Campaign generation complete. Files saved in 'campaign/' and API bodies in 'campaign_api_bodies.json'.")

if __name__ == "__main__":
    generate_campaign()

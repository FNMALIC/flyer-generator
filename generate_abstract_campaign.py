"""
Generate Codees-CM abstract business flyers + social media posts.
3 flyers (abstract_business, 1200x1600) + 3 social posts (abstract_social, 1080x1080)
"""
import os
import io
import json
from flyer_generator import generate_flyer

COMMON = {
    "logo_path": "logo/image.png",
    "primary_color": "#0076BC",
    "accent_color": "#ED1C24",
    "facebook": "Codees CM",
    "whatsapp": "+237 690 000 000",
    "instagram": "@codees_cm",
    "phone": "www.codees-cm.com",
}

campaign_data = [
    # ── FLYERS (abstract_business) ────────────────────────────────────────────
    {
        "id": "flyer_1_community",
        "type": "flyer",
        "params": {
            **COMMON,
            "template_id": "abstract_business",
            "headline": "The Heart of Tech in Cameroon",
            "sub_headline": "CODEES COMMUNITY",
            "tagline": "Connect · Build · Grow",
            "body_text": "Join 1,000+ developers, designers and entrepreneurs building Africa's digital future together.",
            "cta_text": "JOIN FOR FREE",
            
            "features": [
                {"icon": "●", "title": "COMMUNITY",  "desc": "1,000+ devs & builders across Africa"},
                {"icon": "◆", "title": "MENTORSHIP", "desc": "1:1 sessions with industry experts"},
                {"icon": "✉", "title": "EVENTS",     "desc": "Hackathons, workshops & networking"},
            ]
        }
    },
    {
        "id": "flyer_2_mentorship",
        "type": "flyer",
        "params": {
            **COMMON,
            "template_id": "abstract_business",
            "headline": "Scale Your Career With Expert Mentors",
            "sub_headline": "CODEES MENTORSHIP",
            "tagline": "Personalized · Proven · Powerful",
            "body_text": "Get matched with senior engineers, product leaders and founders who have done it before.",
            "cta_text": "APPLY NOW",
            
            "features": [
                {"icon": "●", "title": "1:1 SESSIONS",   "desc": "Weekly calls with your personal mentor"},
                {"icon": "◆", "title": "CAREER PLAN",    "desc": "Custom roadmap designed for you"},
                {"icon": "✉", "title": "NETWORK ACCESS", "desc": "Entry into Codees' elite network"},
            ]
        }
    },
    {
        "id": "flyer_3_incubation",
        "type": "flyer",
        "params": {
            **COMMON,
            "template_id": "abstract_business",
            "headline": "From Idea to MVP — We Back You",
            "sub_headline": "CODEES INCUBATION",
            "tagline": "Pitch · Build · Launch",
            "body_text": "Our 3-month program takes your startup idea and turns it into a market-ready product with real traction.",
            "cta_text": "PITCH YOUR IDEA",
            
            "features": [
                {"icon": "●", "title": "WORKSPACE",   "desc": "State-of-the-art co-working hub"},
                {"icon": "◆", "title": "FUNDING",     "desc": "Angel & grant funding connections"},
                {"icon": "✉", "title": "LAUNCH PREP", "desc": "Demo Day with investors & press"},
            ]
        }
    },

    # ── SOCIAL POSTS (abstract_social, 1080x1080) ─────────────────────────────
    {
        "id": "social_1_community",
        "type": "social",
        "params": {
            **COMMON,
            "template_id": "abstract_social",
            "headline": "Join Codees",
            "sub_headline": "The Heart of Tech in Cameroon",
            "tagline": "Connect · Build · Grow with 1,000+ African Devs",
            "cta_text": "www.codees-cm.com",
            
        }
    },
    {
        "id": "social_2_mentorship",
        "type": "social",
        "params": {
            **COMMON,
            "template_id": "abstract_social",
            "headline": "Get a Mentor",
            "sub_headline": "Codees Mentorship Program",
            "tagline": "1:1 expert guidance to fast-track your career",
            "cta_text": "Apply at codees-cm.com",
            
        }
    },
    {
        "id": "social_3_hackathon",
        "type": "social",
        "params": {
            **COMMON,
            "template_id": "abstract_social",
            "headline": "Hack with Us",
            "sub_headline": "Codees Annual Hackathon",
            "tagline": "Code · Create · Conquer · Win Big Prizes",
            "cta_text": "Register at codees-cm.com",
            
        }
    },
]


def run():
    os.makedirs("campaign/abstract", exist_ok=True)

    api_bodies = {}

    for item in campaign_data:
        print(f"Generating: {item['id']}...")
        img_data = generate_flyer(item["params"])
        fname = f"campaign/abstract/codees_{item['id']}.png"
        with open(fname, "wb") as f:
            f.write(img_data.read())
        api_bodies[item["id"]] = item["params"]
        print(f"  -> Saved: {fname}")

    with open("campaign/abstract/api_bodies.json", "w") as f:
        json.dump(api_bodies, f, indent=4)

    print("\nDone! Files saved in campaign/abstract/")
    print("API bodies saved to campaign/abstract/api_bodies.json")


if __name__ == "__main__":
    run()

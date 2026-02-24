import requests
import json
import os

requests_data = [
    {
        "template": "template 1",
        "headline": "Collectez vos emails, boostez votre business !",
        "body_text": "Démarrez dès aujourd'hui ! Une base de données clients est l'avenir de votre PME.",
        "cta_text": "www.codees-cm.com"
    },
    {
        "template": "template 2",
        "headline": "Collectez vos emails, boostez votre business !",
        "body_text": "Démarrez dès aujourd'hui ! Une base de données clients est l'avenir de votre PME.",
        "cta_text": "www.codees-cm.com"
    },
    {
        "template": "template 3",
        "headline": "Collectez vos emails, boostez votre business !",
        "body_text": "Démarrez dès aujourd'hui ! Une base de données clients est l'avenir de votre PME.",
        "cta_text": "www.codees-cm.com"
    },
    {
        "template": "template 4",
        "headline": "Collectez vos emails, boostez votre business !",
        "body_text": "Démarrez dès aujourd'hui ! Une base de données clients est l'avenir de votre PME.",
        "cta_text": "www.codees-cm.com"
    }
]

url = "http://localhost:5000/generate-flyer"
output_dir = "test_results"
os.makedirs(output_dir, exist_ok=True)

for i, data in enumerate(requests_data, 1):
    print(f"Sending request for template {i}...")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            output_path = os.path.join(output_dir, f"result_template_{i}.png")
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Saved to {output_path}")
        else:
            print(f"Error for template {i}: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to connect for template {i}: {e}")

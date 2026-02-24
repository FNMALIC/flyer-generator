import sys
import json
from PIL import ImageDraw

# Monkey-patch ImageDraw to intercept text calls
original_text = ImageDraw.ImageDraw.text

def text_interceptor(self, xy, text, fill=None, font=None, anchor=None, spacing=4, align='left', direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False, *args, **kwargs):
    print(f"DRAWING TEXT: '{text}' at {xy} with fill={fill}")
    return original_text(self, xy, text, fill=fill, font=font, anchor=anchor, spacing=spacing, align=align, direction=direction, features=features, language=language, stroke_width=stroke_width, stroke_fill=stroke_fill, embedded_color=embedded_color, *args, **kwargs)

ImageDraw.ImageDraw.text = text_interceptor

# Now import flyer_generator
from flyer_generator import generate_flyer

def check(id_name, config):
    print(f"--- Checking {id_name} ---")
    generate_flyer(config)

check("9_projects", {
    "template_id": "codees_minimal",
    "headline": "Building Cameroon's Digital Future, Together",
    "tagline": "Open-source projects powered by the Codees community.",
    "cta_text": "EXPLORE PROJECTS"
})

check("10_impact", {
    "template_id": "codees_hero",
    "headline": "Real Impact. Real Stories.",
    "tagline": "Success · Innovation · Community",
    "image_path": "image.png",
    "cta_text": "www.codees-cm.com"
})

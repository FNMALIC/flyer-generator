from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import textwrap
import os
import json
import math
from config import DEFAULT_CONFIG

def get_font(font_name_or_path, size, bold=False):
    """Try to load a font, fallback to default if not found."""
    try:
        # Check if it's a direct path
        if os.path.exists(str(font_name_or_path)):
            return ImageFont.truetype(str(font_name_or_path), size)
        
        # Try common paths for DejaVuSans
        font_paths = []
        if bold:
             font_paths.append("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        font_paths.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans.ttf"
        ])
        
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
        
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def hex_to_rgb(hex_str):
    if not hex_str: return (0,0,0)
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_brightness(color):
    """Estimate perceived brightness of an RGB color (0-255)."""
    if isinstance(color, str):
        color = hex_to_rgb(color)
    r, g, b = color[:3]
    return (0.299 * r + 0.587 * g + 0.114 * b)

def get_contrast_color(bg_color):
    """Return white or black depending on which has better contrast with bg_color."""
    return "#FFFFFF" if get_brightness(bg_color) < 128 else "#000000"

def draw_drop_shadow(image, shape_func, offset=(10, 10), iterations=10, shadow_color=(0, 0, 0, 100)):
    """
    Draw a drop shadow for a shape.
    shape_func: function that takes a Draw object and draws the shape.
    """
    shadow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    
    # Draw original shape on shadow layer with offset
    # Note: We might need to wrap the shape_func to apply offset
    shape_func(shadow_draw, offset)
    
    # Blur the shadow layer
    for _ in range(iterations):
        shadow_layer = shadow_layer.filter(ImageFilter.BLUR)
    
    # Compose
    image.paste(shadow_layer, (0, 0), shadow_layer)

def draw_accent_line(draw, start, end, color, width=2, opacity=150):
    """Draw a thin, professional-looking accent line."""
    rgb = hex_to_rgb(color) if isinstance(color, str) else color
    draw.line([start, end], fill=(*rgb, opacity) if len(rgb) == 3 else rgb, width=width)

def draw_geometric_pattern(image, color, type="dots"):
    """Draw subtle geometric patterns in the background."""
    draw = ImageDraw.Draw(image, 'RGBA')
    w, h = image.size
    rgb = hex_to_rgb(color) if isinstance(color, str) else color
    fill = (*rgb, 40) # Very subtle
    
    if type == "dots":
        step = 40
        for x in range(0, w, step):
            for y in range(0, h, step):
                draw.ellipse([x, y, x+4, y+4], fill=fill)
    elif type == "lines":
        step = 60
        for i in range(0, w + h, step):
            draw.line([(i, 0), (0, i)], fill=fill, width=1)

def draw_wrapped_text(draw, text, font, color, max_width, x_center, y_start, alignment="center", line_height=1.2):
    if not text: return y_start
    text = str(text).replace('\\n', '\n')
    avg_char_width = font.getlength("x") if hasattr(font, 'getlength') else 10
    chars_per_line = max(1, int(max_width / avg_char_width))
    lines = []
    for section in text.split('\n'):
        if section.strip() == "": lines.append("")
        else: lines.extend(textwrap.wrap(section, width=chars_per_line))
    curr_y = y_start
    line_spacing = font.size * line_height
    for line in lines:
        if line == "":
            curr_y += line_spacing / 2
            continue
        line_width = font.getlength(line)
        if alignment == "left": x = x_center - max_width / 2
        elif alignment == "right": x = x_center + max_width / 2 - line_width
        else: x = x_center - line_width / 2
        draw.text((x, curr_y), line, font=font, fill=color)
        curr_y += line_spacing
    return curr_y

def draw_logo(image, logo_path, position, size=(150, 150)):
    """Helper to draw the logo at a specific position."""
    if not logo_path or not os.path.exists(logo_path):
        return
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail(size, Image.Resampling.LANCZOS)
        # Handle centering if position is (w/2, y)
        if isinstance(position[0], float) or position[0] == image.width / 2:
            x = int(position[0] - logo.width / 2)
        else:
            x = position[0]
        image.paste(logo, (int(x), int(position[1])), logo)
    except Exception as e:
        print(f"Error drawing logo: {e}")

def resize_to_fill(img, target_w, target_h):
    img_w, img_h = img.size
    ratio = max(target_w / img_w, target_h / img_h)
    new_size = (int(img_w * ratio), int(img_h * ratio))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    left = (new_size[0] - target_w) / 2
    top = (new_size[1] - target_h) / 2
    return img.crop((left, top, left + target_w, top + target_h))

def draw_glass_rect(image, xy, fill=(255, 255, 255, 120), blur_radius=20):
    """Draws a 'glass' effect rectangle with background blur."""
    x1, y1, x2, y2 = xy
    # 1. Extract the area to blur
    mask = Image.new('L', (x2-x1, y2-y1), 255)
    region = image.crop((x1, y1, x2, y2))
    # 2. Apply strong blur
    region = region.filter(ImageFilter.GaussianBlur(blur_radius))
    # 3. Add semi-transparent overlay
    overlay = Image.new('RGBA', region.size, fill)
    region = Image.alpha_composite(region.convert('RGBA'), overlay)
    # 4. Paste back
    image.paste(region, (x1, y1))
    # 5. Optional: Add a subtle white border
    draw = ImageDraw.Draw(image, 'RGBA')
    draw.rectangle([x1, y1, x2, y2], outline=(255, 255, 255, 180), width=1)

def draw_feature_item(draw, x, y, title, text, primary_color, secondary_color, width):
    """Draws a feature section with an icon placeholder and text."""
    # Icon placeholder (Circle with a small shape)
    icon_size = 60
    draw.ellipse([x, y, x + icon_size, y + icon_size], fill=primary_color)
    # Simple icon (gear-like)
    for i in range(8):
        # Very simple gear representation
        pass 
    
    # Title
    font_t = get_font("DejaVuSans", 28, bold=True)
    draw.text((x + icon_size + 20, y), title.upper(), font=font_t, fill=secondary_color)
    
    # Body
    font_b = get_font("DejaVuSans", 20)
    draw_wrapped_text(draw, text, font_b, "#666666", width - icon_size - 40, x + icon_size + 20 + (width - icon_size - 40)/2, y + 35, alignment="left")
    
    return y + 150

def render_modern_corporate(ctx):
    """Elite Corporate: Clean, minimalist, white-space focused."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#D35400'))
    secondary = hex_to_rgb(c.get('secondary_color', '#2C3E50'))
    padding = int(w * 0.08)

    # 1. Background
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill="#FFFFFF")
    
    # 2. Main Image (Elegant mask)
    if 'image_path' in c and os.path.exists(c['image_path']):
        img_w, img_h = int(w * 0.8), int(h * 0.45)
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, img_w, img_h)
        # Centered bottom alignment for image
        ix, iy = (w - img_w) / 2, padding * 2
        f.paste(img, (int(ix), int(iy)))

    # 3. Typography (Clean grid)
    curr_y = padding * 2 + int(h * 0.45) + 60
    
    # Headline
    font_h = get_font(c['default_font'], 80, bold=True)
    curr_y = draw_wrapped_text(d, c.get('headline', 'PREMIUM SERVICES').upper(), font_h, secondary, w - 2*padding, w/2, curr_y, alignment="center")
    
    # Accent Line
    curr_y += 20
    draw_accent_line(d, (w/2 - 100, curr_y), (w/2 + 100, curr_y), primary, width=4)
    curr_y += 40
    
    # Tagline
    font_tag = get_font(c['default_font'], 28)
    curr_y = draw_wrapped_text(d, c.get('tagline', 'EXCELLENCE IN EVERY DETAIL'), font_tag, secondary, w - 2*padding, w/2, curr_y, alignment="center")
    
    # 4. Features (Minimalist Grid)
    curr_y += 80
    features = c.get('features', [])
    fw = (w - 2 * padding) / 3
    for i, item in enumerate(features[:3]):
        fx = padding + i * fw
        d.rectangle([fx + fw/2 - 20, curr_y, fx + fw/2 + 20, curr_y + 4], fill=primary)
        font_f = get_font(c['default_font'], 20, bold=True)
        draw_wrapped_text(d, item.get('title', '').upper(), font_f, secondary, fw - 20, fx + fw/2, curr_y + 20)

    # 5. Footer
    font_footer = get_font(c['default_font'], 24, bold=True)
    d.text((padding, h - padding - 40), c.get('company_name', 'CORE').upper(), font=font_footer, fill=secondary)
    d.text((w - padding - 300, h - padding - 40), c.get('cta_text', 'WWW.CORE.COM'), font=font_footer, fill=primary)

def render_marketing_agency(ctx):
    """Premium Agency: High-contrast, bold typography with glassmorphism elements."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#FFC107'))
    secondary = hex_to_rgb(c.get('secondary_color', '#1A1A1A'))
    padding = int(w * 0.08)
    is_landscape = w > h

    # 1. Background (Premium dark gradient feel)
    if not c.get('bg_image_path'):
        # Draw a subtle gradient background manually if no template image
        for i in range(h):
            color = tuple(int(secondary[j] * (0.8 + 0.2 * i / h)) for j in range(3))
            d.line([(0, i), (w, i)], fill=color)
    
    # 2. Main Hero Image
    if 'image_path' in c and os.path.exists(c['image_path']):
        if is_landscape:
            img_w, img_h = int(w * 0.45), h
            ix, iy = w - img_w, 0
        else:
            img_w, img_h = w, int(h * 0.5)
            ix, iy = 0, 0
            
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, img_w, img_h)
        f.paste(img, (ix, iy))
        
        # Add a subtle overlay to the image part
        if not is_landscape:
            overlay = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 40))
            f.paste(overlay, (ix, iy), overlay)

    # 3. Content Area (Glassmorphism if it's over an image)
    content_w = int(w * 0.5) if is_landscape else w
    content_h = h if is_landscape else int(h * 0.6)
    cx, cy = 0, 0 if is_landscape else int(h * 0.4)
    
    if is_landscape:
        draw_glass_rect(f, (0, 0, content_w + 40, h), fill=(*secondary, 220), blur_radius=10)
    else:
        draw_glass_rect(f, (0, cy, w, h), fill=(*secondary, 200), blur_radius=15)

    # 4. Typography
    draw_y = cy + padding
    
    # Headline
    font_h_size = int(h * 0.12) if not is_landscape else int(h * 0.15)
    font_h = get_font(c['default_font'], font_h_size, bold=True)
    headline = c.get('headline', 'BE BOLD.').upper()
    draw_y = draw_wrapped_text(d, headline, font_h, "#FFFFFF", content_w - 2*padding, padding, draw_y, alignment="left", line_height=0.95)
    
    # Tagline/Body
    draw_y += 20
    font_tag = get_font(c['default_font'], int(h * 0.04), bold=True)
    draw_y = draw_wrapped_text(d, c.get('tagline', 'CREATIVE SOLUTIONS').upper(), font_tag, primary, content_w - 2*padding, padding, draw_y, alignment="left")
    
    draw_y += 30
    font_body = get_font(c['default_font'], int(h * 0.03))
    body_text = c.get('body_text', 'Breaking boundaries through minimalist execution and strategic design.')
    draw_wrapped_text(d, body_text, font_body, "#DDDDDD", content_w - 2.5*padding, padding, draw_y, alignment="left", line_height=1.3)

    # 5. Branding Footer
    footer_y = h - padding
    font_cta = get_font(c['default_font'], int(h * 0.035), bold=True)
    cta_text = c.get('cta_text', 'WWW.CODEES-CM.COM').upper()
    d.text((padding, footer_y), cta_text, font=font_cta, fill=primary)
    
    # Accent bar
    d.rectangle([padding, footer_y - 15, padding + 80, footer_y - 10], fill=primary)

def render_zenith_modern(ctx):
    """Zenith v2: Responsive high-end glassmorphism design."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']

    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    accent = hex_to_rgb(c.get('accent_color', '#ED1C24'))
    is_landscape = w > h

    # 1. Background
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill='#0D1B2A')
    
    # 2. Main Hero Image (if provided)
    img_path = c.get('image_path', '')
    if img_path and os.path.exists(img_path):
        img_w, img_h = (int(w * 0.5), h) if is_landscape else (w, int(h * 0.45))
        ix, iy = (w - img_w, 0) if is_landscape else (0, 0)
        img = Image.open(img_path)
        img = resize_to_fill(img, img_w, img_h)
        f.paste(img, (ix, iy))
        
        # Vignette overlay for image
        overlay = Image.new('RGBA', (img_w, img_h), (13, 27, 42, 60))
        f.paste(overlay, (ix, iy), overlay)

    # 3. Glassmorphism Content Card
    if is_landscape:
        card_w, card_h = int(w * 0.6), int(h * 0.8)
        card_x, card_y = int(w * 0.05), int(h * 0.1)
    else:
        card_w, card_h = int(w * 0.9), int(h * 0.65)
        card_x, card_y = int(w * 0.05), int(h * 0.3)

    draw_glass_rect(f, (card_x, card_y, card_x + card_w, card_y + card_h),
                    fill=(255, 255, 255, 25), blur_radius=20)

    # 4. Content inside card
    inner_padding = 60
    curr_x = card_x + inner_padding
    curr_y = card_y + 40
    
    # Logo
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (curr_x, curr_y), size=(200, 80))
    curr_y += 110

    # Headline
    font_h_size = int(card_h * 0.15) if is_landscape else int(card_h * 0.12)
    font_h = get_font(c['default_font'], font_h_size, bold=True)
    headline = c.get('headline', 'ELEVATING STANDARDS').upper()
    curr_y = draw_wrapped_text(d, headline, font_h, "#FFFFFF", card_w - 2*inner_padding, curr_x, curr_y, alignment="left", line_height=0.95)
    
    # Body or Features
    curr_y += 20
    d.rectangle([curr_x, curr_y, curr_x + 60, curr_y + 4], fill=accent)
    curr_y += 20
    
    if c.get('body_text'):
        font_body = get_font(c['default_font'], int(card_h * 0.05))
        draw_wrapped_text(d, c['body_text'], font_body, "#EEEEEE", card_w - 2.5*inner_padding, curr_x, curr_y, alignment="left", line_height=1.4)
    elif c.get('features'):
        font_feat = get_font(c['default_font'], int(card_h * 0.045), bold=True)
        for feat in c['features'][:2]:
            curr_y = draw_wrapped_text(d, f"• {feat['title']}", font_feat, primary, card_w - 2*inner_padding, curr_x, curr_y, alignment="left")
            curr_y += 5

    # Footer/CTA inside card
    footer_y = card_y + card_h - 60
    font_cta = get_font(c['default_font'], int(card_h * 0.05), bold=True)
    cta_text = c.get('cta_text', 'WWW.CODEES-CM.COM').upper()
    d.text((curr_x, footer_y), cta_text, font=font_cta, fill=primary)

def render_codees_minimal(ctx):
    """Codees Clean v2: Sophisticated minimalist design with refined typography."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#0076BC')) # Blue
    accent = hex_to_rgb(c.get('accent_color', '#ED1C24'))   # Red
    padding = int(w * 0.1)
    
    # 1. White Background
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill="#FFFFFF")
    
    # 2. Logo (Centered at top)
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (w/2, 60), size=(250, 120))
    
    # 3. Content Block
    curr_y = 280
    
    # Decorative Top Accent
    d.rectangle([w/2 - 40, curr_y, w/2 + 40, curr_y + 4], fill=accent)
    curr_y += 40
    
    # Headline (Elegant & Balanced)
    font_h_size = int(h * 0.08)
    font_h = get_font(c['default_font'], font_h_size, bold=True)
    headline_color = c.get('headline_font_color', '#1A1A1A')
    curr_y = draw_wrapped_text(d, c.get('headline', 'BUILD THE FUTURE'), font_h, headline_color, w * 0.8, w/2, curr_y, alignment="center", line_height=1.0)
    
    # Body Text (Clean spacing)
    if c.get('body_text'):
        curr_y += 30
        font_body = get_font(c['default_font'], int(h * 0.025))
        body_color = c.get('body_font_color', '#444444')
        curr_y = draw_wrapped_text(d, c['body_text'], font_body, body_color, w * 0.7, w/2, curr_y, alignment="center", line_height=1.5)
    
    # 4. Refined Footer
    footer_y = h - 180
    draw_accent_line(d, (padding, footer_y), (w - padding, footer_y), "#EEEEEE", width=1)
    
    # Contact Details
    contact_y = footer_y + 30
    font_contact = get_font(c['default_font'], int(h * 0.02))
    contact_color = c.get('contact_font_color', '#666666')
    
    contact_parts = []
    if c.get('contact_website'): contact_parts.append(c['contact_website'])
    if c.get('contact_email'): contact_parts.append(c['contact_email'])
    if c.get('contact_phone'): contact_parts.append(c['contact_phone'])
    
    if contact_parts:
        contact_text = "  |  ".join(contact_parts)
        draw_wrapped_text(d, contact_text, font_contact, contact_color, w * 0.9, w/2, contact_y, alignment="center")

    # 5. Subtle Branding Accent
    bar_h = 10
    d.rectangle([0, h - bar_h, w, h], fill=primary)
    d.rectangle([0, h - bar_h - 5, w * 0.3, h - bar_h], fill=accent)

def render_codees_hero(ctx):
    """Codees Hero v2: Full-bleed image, gradient anchor, clean hierarchy."""
    f = ctx['flyer']
    d = ctx['draw']\

    w = ctx['width']
    h = ctx['height']
    c = ctx['config']

    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    accent  = hex_to_rgb(c.get('accent_color',  '#ED1C24'))

    # 1. Hero Image (or dark background)
    img_path = c.get('image_path', '')
    if img_path and os.path.exists(img_path) and not c.get('bg_image_path'):
        img = Image.open(img_path)
        img = resize_to_fill(img, w, h)
        f.paste(img, (0, 0))
    elif not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill='#1A1A2E')

    # 2. Gradient overlay – dark from bottom, fades up (ensures legibility)
    gradient = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for i in range(h):
        alpha = int(220 * (i / h) ** 1.4)   # stronger at bottom
        gd.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
    f.paste(Image.alpha_composite(f.convert('RGBA'), gradient).convert('RGB'), (0, 0))

    # 3. Thin top bar (brand accent, 8 px)
    d.rectangle([0, 0, w, 8], fill=primary)

    # 4. Logo – top-left with safe padding
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (60, 30), size=(160, 90))

    # 5. Headline block – bottom-left anchor
    padding_x = int(w * 0.07)
    baseline  = h - int(h * 0.12)          # 12 % from bottom

    headline  = c.get('headline', 'DIGITAL TRANSFORMATION').upper()
    tagline   = c.get('tagline',  'SUCCESS STORIES FROM AFRICA').upper()

    font_tag  = get_font(c['default_font'], 30, bold=True)
    font_h    = get_font(c['default_font'], 88, bold=True)

    # Small accent category label above headline
    tag_y = baseline - int(font_h.size * 1.2 * len(textwrap.wrap(headline, 16))) - 80
    d.text((padding_x, tag_y), tagline, font=font_tag, fill=(*accent, 255))
    draw_accent_line(d, (padding_x, tag_y + 44), (padding_x + 200, tag_y + 44), accent, width=3)

    # Main headline (white, bold)
    draw_wrapped_text(d, headline, font_h, '#FFFFFF', w * 0.75,
                      padding_x + (w * 0.75) / 2, tag_y + 68,
                      alignment='left', line_height=1.05)

    # 6. Footer strip
    footer_h = int(h * 0.065)
    d.rectangle([0, h - footer_h, w, h], fill=(*primary, 230))
    font_f   = get_font(c['default_font'], 24, bold=True)
    cta      = c.get('cta_text', 'WWW.CODEES-CM.COM').lower()
    cta_w    = font_f.getlength(cta)
    d.text((padding_x, h - footer_h + (footer_h - 28) // 2), 'f  i  in  @codees', font=font_f, fill='#FFFFFF')
    d.text((w - padding_x - cta_w,  h - footer_h + (footer_h - 28) // 2), cta, font=font_f, fill='#FFFFFF')
def render_social_post(ctx):
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#D35400'))
    secondary = hex_to_rgb(c.get('secondary_color', '#2C3E50'))
    padding = int(w * 0.08)

    # 1. Background split
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill="#FFFFFF")
    if c.get('accents_enabled', True):
        draw_geometric_pattern(f, secondary, type="dots")
    
    # 2. Hero Image inside a large geometric frame
    if 'image_path' in c and os.path.exists(c['image_path']):
        img_size = int(w * 0.85)
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, img_size, int(h * 0.5))
        
        ix, iy = int(w * 0.075), int(h * 0.05)
        
        if c.get('shadow_enabled', True):
            def frame_shadow(sd, offset):
                sd.rectangle([ix + offset[0], iy + offset[1], ix + img_size + offset[0], iy + int(h * 0.5) + offset[1]], fill=(0, 0, 0, 80))
            draw_drop_shadow(f, frame_shadow, offset=(15, 15))
            
        f.paste(img, (ix, iy))
        # Accent bar
        d.rectangle([ix, iy + int(h * 0.5), ix + img_size, iy + int(h * 0.5) + 15], fill=primary)

    # 3. Main Headline Block
    curr_y = int(h * 0.6)
    font_h = get_font(c['default_font'], int(w * 0.08), bold=True)
    curr_y = draw_wrapped_text(d, c.get('headline', 'BOOST YOUR GROWTH').upper(), font_h, secondary, w - 2*padding, w/2, curr_y, alignment="center")
    
    curr_y += 20
    font_tag = get_font(c['default_font'], int(w * 0.04), bold=True)
    curr_y = draw_wrapped_text(d, c.get('tagline', 'MODERN SOLUTIONS').upper(), font_tag, primary, w - 2*padding, w/2, curr_y, alignment="center")

    # 4. CTA Button
    btn_w, btn_h = int(w * 0.6), 80
    bx, by = (w - btn_w)/2, h - 180
    
    if c.get('shadow_enabled', True):
        def btn_shadow(sd, offset):
            sd.rectangle([bx + offset[0], by + offset[1], bx + btn_w + offset[0], by + btn_h + offset[1]], fill=(0, 0, 0, 50))
        draw_drop_shadow(f, btn_shadow, offset=(8, 8), iterations=8)
        
    d.rectangle([bx, by, bx + btn_w, by + btn_h], fill=secondary)
    
    font_cta = get_font(c['default_font'], 26, bold=True)
    cta_t = c.get('cta_text', 'LEARN MORE').upper()
    t_width = font_cta.getlength(cta_t)
    d.text((w/2 - t_width/2, by + 25), cta_t, font=font_cta, fill=primary)

    # 5. Decorative corners
    corner_size = 100
    d.line([(0, 0), (corner_size, 0)], fill=primary, width=10)
    d.line([(0, 0), (0, corner_size)], fill=primary, width=10)
    d.line([(w-corner_size, h), (w, h)], fill=secondary, width=10)
    d.line([(w, h-corner_size), (w, h)], fill=secondary, width=10)

def render_abstract_business(ctx):
    """Abstract Business: Bold diagonal + photo + dark panel + feature row."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']

    primary  = hex_to_rgb(c.get('primary_color', '#0076BC'))  # Codees Blue
    accent   = hex_to_rgb(c.get('accent_color',  '#ED1C24'))  # Codees Red
    dark     = (18, 18, 24)

    # ── 1. White base ──────────────────────────────────────────────────────────
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill='#FFFFFF')

    # ── 2. Hero Photo (right side, clipped with diagonal) ──────────────────────
    photo_x = int(w * 0.30)   # photo starts here
    img_path = c.get('image_path', '')
    if img_path and os.path.exists(img_path):
        img = Image.open(img_path)
        img = resize_to_fill(img, w - photo_x, int(h * 0.60))
        # Darken slightly
        ov = Image.new('RGBA', img.size, (0, 0, 0, 50))
        img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
        f.paste(img, (photo_x, 0))
    else:
        d.rectangle([photo_x, 0, w, int(h * 0.60)], fill='#1A2640')

    # ── 3. Diagonal overlay (left accent block) ─────────────────────────────────
    # Yellow/primary diagonal block: covers top-left, angled right
    split_x   = int(w * 0.52)
    split_top = int(h * 0.40)
    d.polygon([
        (0, 0), (split_x, 0),
        (int(w * 0.32), split_top),
        (0, split_top)
    ], fill=primary)

    # ── 4. Company name + logo top-left ────────────────────────────────────────
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (48, 36), size=(200, 90))

    # ── 5. Bold Headline (white, over primary block) ───────────────────────────
    font_h = get_font(c['default_font'], 80, bold=True)
    headline = c.get('headline', 'CODEES\nCOMPANY').upper()
    curr_y = int(h * 0.12)
    for line in textwrap.wrap(headline, width=12):
        d.text((50, curr_y), line, font=font_h, fill='#FFFFFF')
        curr_y += int(font_h.size * 1.1)
    # Red underline accent
    d.rectangle([50, curr_y + 6, 50 + 100, curr_y + 12], fill=accent)

    # ── 6. Geometric ornaments (top-right) ─────────────────────────────────────
    def draw_rotated_square(draw, cx, cy, size, angle_deg, color, alpha=180):
        """Draw a filled rotated square."""
        overlay = Image.new('RGBA', f.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        r = math.radians(angle_deg)
        hs = size / 2
        pts = [
            (cx + hs * math.cos(r + math.pi/4 * i * 2),
             cy + hs * math.sin(r + math.pi/4 * i * 2))
            for i in range(4)
        ]
        od.polygon(pts, fill=(*dark, alpha))
        f.paste(Image.alpha_composite(f.convert('RGBA'), overlay).convert('RGB'), (0, 0))

    # Logo area top-right
    logo_box_x = w - int(w * 0.30)
    logo_box_y = int(h * 0.03)
    logo_box_w = int(w * 0.28)
    # Logo placeholder if no path
    draw_logo(f, logo_path, (logo_box_x + logo_box_w // 2, logo_box_y + 30), size=(180, 80))

    # Decorative rotated squares
    draw_rotated_square(d, w - 60, 80, 70, 20, dark, 200)
    draw_rotated_square(d, w - 110, 130, 45, 35, dark, 150)
    draw_rotated_square(d, w - 40, 160, 30, 50, primary, 200)

    # ── 7. Dark bottom panel ───────────────────────────────────────────────────
    panel_y = int(h * 0.52)
    d.rectangle([0, panel_y, w, h], fill=dark)

    # Centered sub-headline
    sub = c.get('sub_headline', 'ABSTRACT BUSINESS').upper()
    font_sub = get_font(c['default_font'], 52, bold=True)
    sub_w = font_sub.getlength(sub)
    d.text(((w - sub_w) / 2, panel_y + 40), sub, font=font_sub, fill='#FFFFFF')

    # Sub-tagline
    tag = c.get('tagline', 'LOREM IPSUM DOLORES').upper()
    font_tag2 = get_font(c['default_font'], 26)
    tag_w = font_tag2.getlength(tag)
    d.text(((w - tag_w) / 2, panel_y + 108), tag, font=font_tag2, fill=primary)

    # Body text
    body = c.get('body_text', 'Join the fastest-growing tech community in Cameroon. We connect developers, designers, and entrepreneurs to create impact.')
    font_b = get_font(c['default_font'], 22)
    draw_wrapped_text(d, body, font_b, '#CCCCCC', w * 0.76, w / 2, panel_y + 155, alignment='center', line_height=1.5)

    # ── 8. Feature icons row ───────────────────────────────────────────────────
    features = c.get('features') or [
        {'icon': '●', 'title': 'COMMUNITY',    'desc': 'Connect with 1,000+ devs & builders across Africa'},
        {'icon': '◆', 'title': 'MENTORSHIP',   'desc': 'Get paired with industry-leading tech mentors'},
        {'icon': '✉', 'title': 'INCUBATION',   'desc': 'Turn your idea into a funded startup product'},
    ]
    icon_y   = panel_y + int(h * 0.30)
    col_w    = w // len(features)
    for i, feat in enumerate(features[:3]):
        cx = col_w * i + col_w // 2
        # Circle
        r = 38
        d.ellipse([cx - r, icon_y - r, cx + r, icon_y + r], outline=primary, width=3)
        font_ic = get_font(c['default_font'], 34, bold=True)
        ic_char = feat.get('icon', '●')
        ic_w = font_ic.getlength(ic_char)
        d.text((cx - ic_w / 2, icon_y - 24), ic_char, font=font_ic, fill=primary)
        # Title
        font_it = get_font(c['default_font'], 22, bold=True)
        it_w = font_it.getlength(feat['title'])
        d.text((cx - it_w / 2, icon_y + r + 12), feat['title'], font=font_it, fill='#FFFFFF')
        # Desc
        font_id = get_font(c['default_font'], 18)
        draw_wrapped_text(d, feat.get('desc', ''), font_id, '#AAAAAA', col_w - 40, cx, icon_y + r + 46, alignment='center', line_height=1.35)

    # ── 9. Social footer strip ─────────────────────────────────────────────────
    footer_h = int(h * 0.052)
    footer_y = h - footer_h
    d.rectangle([0, footer_y, w, h], fill=primary)
    font_f   = get_font(c['default_font'], 20, bold=True)
    socials  = [
        ('f', c.get('facebook',  '@codees')),
        ('w', c.get('whatsapp', '+237 600 000 000')),
        ('in', c.get('instagram', '@codees_cm')),
        ('☎', c.get('phone',     'www.codees-cm.com')),
    ]
    seg_w  = w // len(socials)
    for i, (icon, label) in enumerate(socials):
        sx  = seg_w * i + seg_w // 2
        txt = f'{icon}  {label}'
        tw  = font_f.getlength(txt)
        d.text((sx - tw / 2, footer_y + (footer_h - 24) // 2), txt, font=font_f, fill='#FFFFFF')


def render_abstract_social(ctx):
    """Abstract Social (1080x1080): Compact agency style for Instagram/LinkedIn."""
    # Force square dimensions
    w = 1080
    h = 1080
    ctx['width']  = w
    ctx['height'] = h
    ctx['flyer']  = Image.new('RGB', (w, h), '#FFFFFF')
    ctx['draw']   = ImageDraw.Draw(ctx['flyer'])
    f = ctx['flyer']
    d = ctx['draw']
    c = ctx['config']

    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    accent  = hex_to_rgb(c.get('accent_color',  '#ED1C24'))
    dark    = (18, 18, 24)

    # 1. White base
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill='#FFFFFF')

    # 2. Hero photo (top 55%)
    photo_h = int(h * 0.55)
    img_path = c.get('image_path', '')
    if img_path and os.path.exists(img_path):
        img = Image.open(img_path)
        img = resize_to_fill(img, w, photo_h)
        ov  = Image.new('RGBA', img.size, (0, 0, 0, 60))
        img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
        f.paste(img, (0, 0))
    else:
        d.rectangle([0, 0, w, photo_h], fill='#1A2640')

    # 3. Primary diagonal block (covers top-left)
    diag_w = int(w * 0.55)
    diag_h = int(h * 0.38)
    d.polygon([
        (0, 0), (diag_w, 0),
        (int(w * 0.38), diag_h),
        (0, diag_h)
    ], fill=primary)

    # 4. Logo top-left (on primary block)
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (40, 28), size=(180, 80))

    # 5. Headline (on blue block)
    font_h   = get_font(c['default_font'], 70, bold=True)
    headline = c.get('headline', 'JOIN CODEES').upper()
    curr_y   = int(h * 0.10)
    for line in textwrap.wrap(headline, width=10):
        d.text((44, curr_y), line, font=font_h, fill='#FFFFFF')
        curr_y += int(font_h.size * 1.08)
    d.rectangle([44, curr_y + 6, 44 + 80, curr_y + 12], fill=accent)

    # 6. Top-right ornaments
    def draw_diamond(cx_, cy_, size_, color_):
        pts = [(cx_, cy_ - size_), (cx_ + size_, cy_), (cx_, cy_ + size_), (cx_ - size_, cy_)]
        d.polygon(pts, fill=color_)
    draw_diamond(w - 55, 55, 48, (*dark, 200))
    draw_diamond(w - 100, 110, 30, (*dark, 140))
    draw_diamond(w - 32, 120, 22, (*primary, 220))

    # 7. Dark bottom panel
    panel_y = int(h * 0.52)
    d.rectangle([0, panel_y, w, h], fill=dark)

    # Sub-headline centered
    sub      = c.get('sub_headline', c.get('headline', 'CODEES COMMUNITY')).upper()
    font_sub = get_font(c['default_font'], 46, bold=True)
    sub_w    = font_sub.getlength(sub)
    # Wrap if needed
    sub_lines = textwrap.wrap(sub, width=18)
    sy = panel_y + 30
    for sl in sub_lines:
        slw = font_sub.getlength(sl)
        d.text(((w - slw) / 2, sy), sl, font=font_sub, fill='#FFFFFF')
        sy += int(font_sub.size * 1.1)

    # Tagline
    tag      = c.get('tagline', "Cameroon's Premier Tech Community")
    font_tag2 = get_font(c['default_font'], 26)
    draw_wrapped_text(d, tag, font_tag2, primary, w * 0.8, w / 2, sy + 10, alignment='center', line_height=1.4)

    # 8. CTA button area
    cta_txt  = c.get('cta_text', 'www.codees-cm.com').lower()
    font_cta = get_font(c['default_font'], 26, bold=True)
    cta_w    = int(font_cta.getlength(cta_txt)) + 60
    cta_x    = (w - cta_w) // 2
    cta_y    = h - int(h * 0.155)
    d.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + 56], radius=8, fill=primary)
    tw2 = font_cta.getlength(cta_txt)
    d.text((cta_x + (cta_w - tw2) / 2, cta_y + 14), cta_txt, font=font_cta, fill='#FFFFFF')

    # 9. Social handles footer
    footer_h2 = int(h * 0.062)
    fy2       = h - footer_h2
    d.rectangle([0, fy2, w, h], fill=primary)
    font_f2   = get_font(c['default_font'], 21, bold=True)
    socials   = [('f', c.get('facebook', '@codees')), ('in', c.get('instagram', '@codees_cm'))]
    seg2      = w // (len(socials) + 1)
    for i, (icon, label) in enumerate(socials, 1):
        txt2 = f'{icon}  {label}'
        tw3  = font_f2.getlength(txt2)
        d.text((seg2 * i - tw3 / 2, fy2 + (footer_h2 - 26) // 2), txt2, font=font_f2, fill='#FFFFFF')

    # Copy back to ctx
    ctx['flyer'] = f



def generate_flyer(params):
    config = DEFAULT_CONFIG.copy()
    config.update(params)
    
    # Map template names to template_ids
    template_mapping = {
        'template_1': 'marketing_agency',
        'template_2': 'social_post', 
        'template_3': 'zenith_modern',
        'template_4': 'codees_minimal',
        'logo': 'codees_hero'
    }
    
    # If template is specified, map it to template_id
    if 'template' in params:
        template_name = str(params['template']).strip().lower().replace(" ", "_")
        
        # Check for direct match or variations
        target_key = None
        if template_name in template_mapping:
            target_key = template_name
        elif f"template_{template_name}" in template_mapping:
            target_key = f"template_{template_name}"
            
        if target_key:
            config['template_id'] = template_mapping[target_key]
            print(f"DEBUG: Template '{params['template']}' normalized to '{template_name}' and mapped to template_id '{config['template_id']}'")
            
            # Resolve template image path if not already provided as background
            if not config.get('bg_image_path'):
                template_img_path = os.path.join(os.path.dirname(__file__), 'template', f"{target_key}.png")
                if os.path.exists(template_img_path):
                    config['bg_image_path'] = template_img_path
                    print(f"DEBUG: Using template image: {template_img_path}")
        else:
            print(f"DEBUG: Template '{params['template']}' (normalized: '{template_name}') not found in mapping")
    else:
        print("DEBUG: No template parameter found")
    
    if isinstance(config.get('features'), str):
        try: config['features'] = json.loads(config['features'])
        except: pass

    width = int(config['flyer_width'])
    height = int(config['flyer_height'])
    
    tid = config.get('template_id')
    
    # Auto-adjust dimensions for social media if not provided
    if tid == 'social_post' and 'flyer_width' not in params:
        width = 1080
        height = 1080
        
    bg_path = config.get('bg_image_path')
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert('RGB')
            flyer = resize_to_fill(bg_img, width, height)
        except Exception as e:
            print(f"Error loading background image: {e}")
            flyer = Image.new('RGB', (width, height), config['bg_color'])
    else:
        flyer = Image.new('RGB', (width, height), config['bg_color'])
        
    draw = ImageDraw.Draw(flyer)
    
    ctx = {'flyer': flyer, 'draw': draw, 'width': width, 'height': height, 'config': config}

    if tid == 'marketing_agency':
        print("DEBUG: Calling render_marketing_agency")
        render_marketing_agency(ctx)
    elif tid == 'social_post':
        print("DEBUG: Calling render_social_post")
        render_social_post(ctx)
    elif tid == 'zenith_modern':
        print("DEBUG: Calling render_zenith_modern")
        render_zenith_modern(ctx)
    elif tid == 'codees_minimal':
        print("DEBUG: Calling render_codees_minimal")
        render_codees_minimal(ctx)
    elif tid == 'codees_hero':
        print("DEBUG: Calling render_codees_hero")
        render_codees_hero(ctx)
    elif tid == 'abstract_business':
        print("DEBUG: Calling render_abstract_business")
        render_abstract_business(ctx)
    elif tid == 'abstract_social':
        print("DEBUG: Calling render_abstract_social")
        render_abstract_social(ctx)
        # pick updated flyer from ctx after social template resizes it
        flyer = ctx['flyer']
    else:
        print(f"DEBUG: No matching template_id '{tid}', calling render_zenith_modern (fallback)")
        render_zenith_modern(ctx)

    img_byte_arr = io.BytesIO()
    flyer.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr.seek(0)
    return img_byte_arr

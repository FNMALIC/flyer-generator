from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import textwrap
import os
import json
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
    """Bold Minimalist: High-contrast, Swiss-inspired design."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#FFC107'))
    secondary = hex_to_rgb(c.get('secondary_color', '#1A1A1A'))
    padding = int(w * 0.1)

    # 1. Background (Bold split)
    d.rectangle([0, 0, w, h], fill=secondary)
    
    # 2. Large Typography (Hero)
    curr_y = padding * 1.5
    font_h = get_font(c['default_font'], 120, bold=True)
    curr_y = draw_wrapped_text(d, c.get('headline', 'BE BOLD.').upper(), font_h, "#FFFFFF", w - 2*padding, padding, curr_y, alignment="left", line_height=1.0)
    
    # 3. Main Image (Square & Minimal)
    if 'image_path' in c and os.path.exists(c['image_path']):
        img_size = int(w * 0.6)
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, img_size, img_size)
        f.paste(img, (int(w - img_size - padding), int(curr_y + 40)))

    # 4. Secondary Content
    curr_y += 100
    font_tag = get_font(c['default_font'], 40, bold=True)
    curr_y = draw_wrapped_text(d, c.get('tagline', 'CREATIVE SOLUTIONS').upper(), font_tag, primary, w*0.4, padding, curr_y, alignment="left")
    
    # Elegant body text
    curr_y += 40
    font_body = get_font(c['default_font'], 22)
    draw_wrapped_text(d, c.get('body_text', 'Breaking boundaries through minimalist execution and strategic design.'), font_body, "#BBBBBB", w*0.35, padding, curr_y, alignment="left")

    # 5. Accent geometries
    d.rectangle([padding, h - padding - 60, padding + 100, h - padding - 55], fill=primary)
    
    font_cta = get_font(c['default_font'], 28, bold=True)
    d.text((padding, h - padding - 40), c.get('cta_text', 'WWW.AGENCY.COM'), font=font_cta, fill="#FFFFFF")

def render_zenith_modern(ctx):
    """Zenith: High-end minimalist design with glassmorphism and full-bleed image."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#D35400'))
    secondary = hex_to_rgb(c.get('secondary_color', '#2C3E50'))
    
    # 1. Full-bleed Background Image with Vignette
    if 'image_path' in c and os.path.exists(c['image_path']):
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, w, h)
        # Apply a dark overlay vignette
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        f.paste(img, (0, 0))
    else:
        d.rectangle([0, 0, w, h], fill="#2C3E50")

    # 2. Large Minimalist Title (Directly on image, or on glass)
    padding = int(w * 0.1)
    
    # Glassmorphism Card
    card_w = int(w * 0.45)
    card_h = int(h * 0.7)
    card_x = padding
    card_y = (h - card_h) / 2
    
    draw_glass_rect(f, (int(card_x), int(card_y), int(card_x + card_w), int(card_y + card_h)), fill=(255, 255, 255, 40))
    
    # 3. Content in Glass Card
    cy = card_y + 80
    
    # Company Name
    font_c = get_font(c['default_font'], 32, bold=True)
    d.text((card_x + 60, cy), c.get('company_name', 'CORE').upper(), font=font_c, fill="#FFFFFF")
    cy += 60
    
    # Vertical accent line
    d.rectangle([card_x + 60, cy, card_x + 64, cy + 300], fill=primary)
    
    # Headline (Bold, high-impact)
    font_h = get_font(c['default_font'], 70, bold=True)
    cy = draw_wrapped_text(d, c.get('headline', 'ZENITH\nDESIGN').upper(), font_h, "#FFFFFF", card_w - 120, card_x + 85, cy + 20, alignment="left", line_height=1.1)
    
    # Tagline
    font_tag = get_font(c['default_font'], 24)
    d.text((card_x + 85, cy + 40), c.get('tagline', 'MINIMALISM DEFINED'), font=font_tag, fill=primary)
    
    # 4. Features (Minimalist dots)
    cy = card_y + card_h * 0.65
    features = c.get('features', [])
    for item in features[:3]:
        # Minimalist dot
        d.ellipse([card_x + 85, cy + 10, card_x + 95, cy + 20], fill=primary)
        font_f = get_font(c['default_font'], 18, bold=True)
        d.text((card_x + 115, cy), item.get('title', '').upper(), font=font_f, fill="#FFFFFF")
        cy += 40

    # 5. Bottom Call to Action (Floating on glass)
    draw_accent_line(d, (card_x + 60, card_y + card_h - 100), (card_x + card_w - 60, card_y + card_h - 100), "#FFFFFF", opacity=100)
    font_cta = get_font(c['default_font'], 22, bold=True)
    d.text((card_x + 85, card_y + card_h - 70), c.get('cta_text', 'WWW.ZENITH.COM'), font=font_cta, fill="#FFFFFF")
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

def generate_flyer(params):
    config = DEFAULT_CONFIG.copy()
    config.update(params)
    
    if isinstance(config.get('features'), str):
        try: config['features'] = json.loads(config['features'])
        except: pass

    width = int(config['flyer_width'])
    height = int(config['flyer_height'])
    
    flyer = Image.new('RGB', (width, height), config['bg_color'])
    draw = ImageDraw.Draw(flyer)
    
    ctx = {'flyer': flyer, 'draw': draw, 'width': width, 'height': height, 'config': config}
    
    tid = config.get('template_id')
    
    # Auto-adjust dimensions for social media if not provided
    if tid == 'social_post' and 'flyer_width' not in params:
        width = 1080
        height = 1080
        ctx['width'] = 1080
        ctx['height'] = 1080
        flyer = Image.new('RGB', (width, height), config['bg_color'])
        ctx['flyer'] = flyer
        ctx['draw'] = ImageDraw.Draw(flyer)

    if tid == 'marketing_agency':
        render_marketing_agency(ctx)
    elif tid == 'social_post':
        render_social_post(ctx)
    elif tid == 'zenith_modern':
        render_zenith_modern(ctx)
    else:
        render_modern_corporate(ctx)

    img_byte_arr = io.BytesIO()
    flyer.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr.seek(0)
    return img_byte_arr

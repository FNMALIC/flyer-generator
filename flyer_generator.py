from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import textwrap
import os
import json
import math
from config import DEFAULT_CONFIG

# Global font cache to speed up dynamic scaling
_FONT_CACHE = {}

def get_font(font_name_or_path, size, bold=False):
    """Try to load a font, with caching for performance."""
    cache_key = (str(font_name_or_path), size, bold)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
        
    try:
        # Check if it's a direct path
        if os.path.exists(str(font_name_or_path)):
            font = ImageFont.truetype(str(font_name_or_path), size)
        else:
            # Try common paths for DejaVuSans
            font_paths = []
            if bold:
                 font_paths.append("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
            font_paths.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "DejaVuSans.ttf"
            ])
            
            font = ImageFont.load_default()
            for path in font_paths:
                try:
                    font = ImageFont.truetype(path, size)
                    break
                except:
                    continue
                    
        _FONT_CACHE[cache_key] = font
        return font
    except Exception:
        return ImageFont.load_default()

def calculate_optimal_font_size(draw, text, font_path, max_width, max_height, initial_size, bold=True, min_size=12):
    """Iteratively find the best font size to fit a box."""
    current_size = initial_size
    while current_size >= min_size:
        font = get_font(font_path, current_size, bold=bold)
        # Simulate drawing to check height
        # We use a dummy y_start and alignment since we only care about the delta_y
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1))) # Lightweight dummy
        # Actually, draw_wrapped_text returns the NEXT y_start
        # So height = returned_y - 0
        height = draw_wrapped_text(temp_draw, text, font, "#000", max_width, 0, 0)
        
        if height <= max_height:
            return current_size
        current_size -= 4 if current_size > 40 else 2
        
    return min_size

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
    if isinstance(color, str):
        fill = (*hex_to_rgb(color), 40)
    elif len(color) == 3:
        fill = (*color, 40)
    else:
        fill = color
    
    if type == "dots":
        step = 40
        for x in range(0, w, step):
            for y in range(0, h, step):
                draw.ellipse([x, y, x+4, y+4], fill=fill)
    elif type == "lines":
        step = 60
        for i in range(0, w + h, step):
            draw.line([(i, 0), (0, i)], fill=fill, width=1)

def draw_wrapped_text(draw, text, font, color, max_width, x_pos, y_start, alignment="center", line_height=1.2):
    """
    Draw wrapped text bounded by max_width.
    x_pos: The reference x position according to alignment.
    Alignment: "left" (x_pos is left), "center" (x_pos is center), "right" (x_pos is right).
    """
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
        if alignment == "left":   x = x_pos
        elif alignment == "right": x = x_pos - line_width
        else:                      x = x_pos - line_width / 2
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

def draw_social_pills(draw, config, w, h, start_y, alignment="center", padding=None):
    """
    Draw a series of premium branded pills for social handles and contacts.
    """
    primary = hex_to_rgb(config.get('primary_color', '#0076BC'))
    font_name = config.get('default_font', 'DejaVuSans')
    
    # Collect items
    items = []
    if config.get('contact_website'): items.append(('🔗', config['contact_website']))
    if config.get('contact_email'):   items.append(('✉', config['contact_email']))
    items.append(('in f', '@codees_cm'))
    
    font_icon = get_font(font_name, int(h * 0.018), bold=True)
    font_label = get_font(font_name, int(h * 0.018))
    
    # Calculate geometries
    total_w = 0
    geoms = []
    gap = 15
    for icon, label in items:
        iw = font_icon.getlength(icon)
        lw = font_label.getlength(label)
        pw = iw + lw + 50
        geoms.append((pw, iw, lw))
        total_w += pw + gap
    total_w -= gap
    
    # Alignment
    if padding is None: padding = int(w * 0.08)
    
    if alignment == "left":
        curr_x = padding
    elif alignment == "right":
        curr_x = w - padding - total_w
    else: # center
        curr_x = (w - total_w) / 2
        
    for i, (icon, label) in enumerate(items):
        pw, iw, lw = geoms[i]
        ph = 42
        
        # Pill Background
        draw.rounded_rectangle([curr_x, start_y, curr_x + pw, start_y + ph], radius=ph/2, fill=primary)
        
        # Icon & Label
        draw.text((curr_x + 20, start_y + 8), icon, font=font_icon, fill="#FFFFFF")
        draw.text((curr_x + 20 + iw + 10, start_y + 8), label, font=font_label, fill="#FFFFFF")
        
        curr_x += pw + gap
    
    return start_y + 50

def draw_complex_footer(image, draw, config, w, h, footer_h=180):
    """
    Draw a sophisticated, multi-column footer inspired by professional marketing flyers.
    """
    primary = hex_to_rgb(config.get('primary_color', '#0076BC'))
    accent = hex_to_rgb(config.get('accent_color', '#ED1C24'))
    font_name = config.get('default_font', 'DejaVuSans')
    
    footer_y = h - footer_h
    
    # 1. Background Strip
    draw.rectangle([0, footer_y, w, h], fill=primary)
    
    # 2. Diagonal Accent (Darker overlay on the right)
    try:
        r, g, b = primary
        dark_primary = (max(0, r-30), max(0, g-30), max(0, b-30))
        slant_x = w * 0.6
        draw.polygon([(slant_x, footer_y), (w, footer_y), (w, h), (slant_x - 50, h)], fill=dark_primary)
    except:
        pass

    pad_x = 40
    pad_y = 35
    
    font_ic = get_font(font_name, 22, bold=True)
    font_text = get_font(font_name, 20)
    font_bold = get_font(font_name, 22, bold=True)
    
    # Left Section: Website & Address
    curr_x = pad_x
    curr_y = footer_y + pad_y
    
    # Website
    draw.text((curr_x + 5, curr_y + 8), "🌐", font=font_ic, fill="#FFFFFF")
    draw.text((curr_x + 50, curr_y + 8), config.get('contact_website', 'www.codees-cm.com'), font=font_text, fill="#FFFFFF")
    
    # Address
    curr_y += 55
    draw.text((curr_x + 5, curr_y + 8), "📍", font=font_ic, fill="#FFFFFF")
    draw.text((curr_x + 50, curr_y + 8), config.get('contact_address', 'Yaoundé, Cameroon'), font=font_text, fill="#FFFFFF")

    # Middle Section: Actual Logo (Transparent background)
    logo_path = config.get('logo_path', 'logo/image.png')
    if os.path.exists(logo_path):
        qr_size = 120
        qr_x = int((w - qr_size) / 2)
        qr_y = int(footer_y + (footer_h - qr_size) / 2)
        
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((qr_size, qr_size), Image.Resampling.LANCZOS)
            image.paste(logo, (int(qr_x + (qr_size - logo.width)/2), int(qr_y + (qr_size - logo.height)/2)), logo)
        except Exception as e:
            print(f"Footer logo error: {e}")
            draw.text((qr_x + 15, qr_y + 40), "CODEES", font=get_font(font_name, 18, bold=True), fill="#FFFFFF")

    # Right Section: Call Us
    curr_x = w * 0.65
    curr_y = footer_y + (footer_h - 60) / 2 + 10
    
    draw.text((curr_x + 5, curr_y + 10), "📞", font=get_font(font_name, 35, bold=True), fill="#FFFFFF")
    
    draw.text((curr_x + 70, curr_y + 2), "CALL US FOR INFO:", font=get_font(font_name, 18, bold=True), fill="#FFFFFF")
    draw.text((curr_x + 70, curr_y + 28), "620181113", font=font_bold, fill="#FFFFFF")

    return footer_y

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
    draw_wrapped_text(draw, text, font_b, "#666666", width - icon_size - 40, x + icon_size + 20, y + 35, alignment="left")
    
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
    d.text((padding, h - padding - 20), c.get('company_name', 'CORE').upper(), font=font_footer, fill=secondary)
    
    draw_social_pills(d, c, w, h, h - padding - 65, alignment="center")
    
    cta_text = c.get('cta_text', 'www.codees-cm.com')
    d.text((w - padding - font_footer.getlength(cta_text), h - padding - 20), cta_text, font=font_footer, fill=primary)

def render_marketing_agency(ctx):
    """Premium Agency v2: High-contrast, bold typography with refined glassmorphism."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#FFC107'))
    secondary = hex_to_rgb(c.get('secondary_color', '#1A1A1A'))
    padding = int(w * 0.08)
    is_landscape = w > h

    # 0. State Detection
    bg_path = c.get('bg_image_path', '')
    is_template_bg = 'template' in bg_path or 'logo' in bg_path

    # 1. Background Enhancement (Gradient + Pattern)
    if not bg_path:
        for i in range(h):
            color = tuple(int(secondary[j] * (0.7 + 0.3 * i / h)) for j in range(3))
            d.line([(0, i), (w, i)], fill=color)
        draw_geometric_pattern(f, (*primary, 20), type="lines")
    
    # Branded Header Box (To fill empty space at the top)
    header_h = 140
    d.rectangle([0, 0, w, header_h], fill="#FFFFFF")
    d.rectangle([0, header_h - 10, w, header_h], fill=primary)
    
    # Logo in the Header
    logo_path = c.get('logo_path', 'logo/image.png')
    draw_logo(f, logo_path, (w/2, header_h/2 - 5), size=(200, 80))
    
    # 2. Hero Image
    if 'image_path' in c and os.path.exists(c['image_path']):
        img_w, img_h = (int(w * 0.45), h - header_h) if is_landscape else (w, int(h * 0.4))
        ix, iy = (w - img_w, header_h) if is_landscape else (0, header_h)
            
        img = Image.open(c['image_path'])
        img = resize_to_fill(img, img_w, img_h)
        f.paste(img, (ix, iy))
        
        # Subtle overlay
        overlay = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 60))
        f.paste(overlay, (ix, iy), overlay)

    # 4. Typography (Dynamic Scaling)
    content_w = int(w * 0.5) if is_landscape else w
    draw_y = header_h + int(padding * 0.8) if not is_landscape else padding
    content_y_start = header_h if not is_landscape else 0
    content_h_adjusted = h - header_h if not is_landscape else h
    
    if not is_template_bg:
        if is_landscape:
            draw_glass_rect(f, (0, 0, content_w + 30, h), fill=(*secondary, 230), blur_radius=15)
        else:
            draw_glass_rect(f, (0, header_h, w, h), fill=(*secondary, 220), blur_radius=20)

    draw_y = content_y_start + padding
    content_w_inner = content_w - 2*padding
    max_h_headline = int(content_h_adjusted * 0.35)
    
    # Dynamic Headline (More conservative initial size for portrait)
    font_h_init = int(h * 0.12) if is_landscape else int(h * 0.085)
    h_size = calculate_optimal_font_size(d, c.get('headline', 'BE BOLD.'), c['default_font'], 
                                       content_w_inner, max_h_headline, font_h_init)
    font_h = get_font(c['default_font'], h_size, bold=True)
    
    headline = c.get('headline', 'BE BOLD.').upper()
    text_color_h = "#1A1A1A" if is_template_bg else "#FFFFFF"
    draw_y = draw_wrapped_text(d, headline, font_h, text_color_h, content_w_inner, padding, draw_y, alignment="left", line_height=0.85)
    
    # Accent Detail
    curr_y = draw_y + 12
    d.rectangle([padding, curr_y, padding + 60, curr_y + 4], fill=primary)
    draw_y = curr_y + 35
    
    # Tagline/Body (Dynamic)
    tagline = c.get('tagline', '').upper()
    if tagline:
        font_tag = get_font(c['default_font'], int(h * 0.035), bold=True)
        draw_y = draw_wrapped_text(d, tagline, font_tag, primary, content_w_inner, padding, draw_y, alignment="left")
    
    body_text = c.get('body_text', '')
    if body_text:
        draw_y += 15
        # Calculate remaining height for body
        max_h_body = h - padding - 60 - draw_y
        body_size = calculate_optimal_font_size(d, body_text, c['default_font'], 
                                              content_w_inner, max_h_body, int(h * 0.028), bold=False, min_size=18)
        font_body = get_font(c['default_font'], body_size)
        text_color_b = "#444444" if is_template_bg else "#DDDDDD"
        draw_wrapped_text(d, body_text, font_body, text_color_b, content_w_inner, padding, draw_y, alignment="left", line_height=1.4)

    # 5. Branded Footer (Professional Complex Layout)
    draw_complex_footer(f, d, c, w, h, footer_h=200)

def render_zenith_modern(ctx):
    """Zenith v3: Premium Aesthetic - Asset-aware, vertically balanced, and pattern-enriched."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']

    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    accent = hex_to_rgb(c.get('accent_color', '#ED1C24'))
    secondary = hex_to_rgb(c.get('secondary_color', '#1A1A1A'))
    is_landscape = w > h

    # 0. State Detection
    img_path = c.get('image_path', '')
    has_hero_img = bool(img_path and os.path.exists(img_path))
    bg_path = c.get('bg_image_path', '')
    is_template_bg = 'template' in bg_path or 'logo' in bg_path
    is_light = c.get('bg_color', '').upper() == '#FFFFFF' or is_template_bg

    # 1. Background Enhancement
    if not bg_path:
        base_fill = '#FFFFFF' if is_light else '#0D1B2A'
        d.rectangle([0, 0, w, h], fill=base_fill)
        if not has_hero_img:
            # Add patterns to image-less background to avoid "dead space"
            draw_geometric_pattern(f, (*primary, 30), type="dots")
            if not is_light:
                # Add a subtle vignette gradient
                for i in range(h):
                    alpha = int(40 * (i / h))
                    d.line([(0, i), (w, i)], fill=(*primary, alpha))
        
        # Branded Header Box (To fill empty space at the top)
        header_h = 140
        d.rectangle([0, 0, w, header_h], fill="#FFFFFF")
        d.rectangle([0, header_h - 10, w, header_h], fill=primary)
        
        # Logo in the Header
        logo_path = c.get('logo_path', 'logo/image.png')
        draw_logo(f, logo_path, (w/2, header_h/2 - 5), size=(200, 80))

    # 2. Main Hero Image (if provided)
    if has_hero_img:
        header_h = 140
        img_w, img_h = (int(w * 0.5), h - header_h) if is_landscape else (w, int(h * 0.4) - header_h)
        ix, iy = (w - img_w, header_h) if is_landscape else (0, header_h)
        img = Image.open(img_path)
        img = resize_to_fill(img, img_w, img_h)
        f.paste(img, (ix, iy))
        
        # Premium vignette overlay
        overlay = Image.new('RGBA', (img_w, img_h), (13, 27, 42, 80))
        f.paste(overlay, (ix, iy), overlay)

    # 3. Glassmorphism Content Card (Smart Centering)
    if is_landscape:
        card_w, card_h = int(w * 0.55), int(h * 0.85)
        card_x = int(w * 0.05)
        card_y = (h - card_h) // 2
    else:
        card_w, card_h = int(w * 0.92), int(h * 0.65)
        card_x = (w - card_w) // 2
        # Center vertically if no hero image, otherwise anchor below image
        card_y = (h - card_h) // 2 if not has_hero_img else int(h * 0.32)

    # Multi-layered glass for premium feel
    if not is_template_bg:
        card_fill = (15, 23, 42, 230) if is_light else (255, 255, 255, 35)
        draw_glass_rect(f, (card_x, card_y, card_x + card_w, card_y + card_h),
                        fill=card_fill, blur_radius=25)

    # 4. Content inside card (Dynamic Typography)
    inner_padding = int(card_w * 0.1)
    curr_x = card_x + inner_padding
    curr_y = card_y + int(card_h * 0.08)
    text_color = "#1A1A1A" if is_template_bg else "#FFFFFF"

    # Headline Start
    curr_y = card_y + int(card_h * 0.12)

    # Dynamic Headline (Tighter constraints)
    max_h_h = int(card_h * 0.35)
    h_init = int(card_h * 0.14) if is_landscape else int(card_h * 0.10)
    headline = c.get('headline', 'ELEVATING STANDARDS').upper()
    h_size = calculate_optimal_font_size(d, headline, c['default_font'], 
                                       card_w - 2*inner_padding, max_h_h, h_init)
    font_h = get_font(c['default_font'], h_size, bold=True)
    curr_y = draw_wrapped_text(d, headline, font_h, text_color, card_w - 2*inner_padding, curr_x, curr_y, alignment="left", line_height=0.85)
    
    # Accent Line
    curr_y += 15
    d.rectangle([curr_x, curr_y, curr_x + 80, curr_y + 4], fill=accent)
    curr_y += 25
    
    # Tagline (Dynamic)
    if c.get('tagline'):
        font_tag = get_font(c['default_font'], int(card_h * 0.05), bold=True)
        tag_color = primary if is_template_bg else accent
        curr_y = draw_wrapped_text(d, c['tagline'], font_tag, tag_color, card_w - 2 * inner_padding, curr_x, curr_y, alignment="left")
        curr_y += 15

    # Dynamic Body / Features
    if c.get('features'):
        features = c.get('features')
        curr_y += 10
        for feat in features[:3]:
            # Feature Icon
            font_ic = get_font(c['default_font'], int(card_h * 0.04), bold=True)
            text_color_ic = primary if is_template_bg else accent
            d.text((curr_x, curr_y), "✓", font=font_ic, fill=text_color_ic)
            
            # Title
            font_it = get_font(c['default_font'], int(card_h * 0.04), bold=True)
            text_color_ft = "#1A1A1A" if is_template_bg else "#FFFFFF"
            # Offset text to the right of the icon
            d.text((curr_x + 35, curr_y), feat['title'], font=font_it, fill=text_color_ft)
            curr_y += int(font_it.size * 1.5)
        curr_y += 10
        
    elif c.get('body_text'):
        max_h_b = card_y + card_h - int(card_h * 0.15) - curr_y
        b_size = calculate_optimal_font_size(d, c['body_text'], c['default_font'], 
                                           card_w - 2*inner_padding, max_h_b, int(card_h * 0.045), bold=False, min_size=16)
        font_body = get_font(c['default_font'], b_size)
        body_color = "#444444" if is_template_bg else "#DDDDDD"
        draw_wrapped_text(d, c['body_text'], font_body, body_color, card_w - 2*inner_padding, curr_x, curr_y, alignment="left", line_height=1.4)

    # 5. Branded Footer (Professional Complex Layout)
    draw_complex_footer(f, d, c, w, h, footer_h=200)

def render_codees_minimal(ctx):
    """Codees Clean v3: Sophisticated minimalist design, asset-aware and balanced."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    accent = hex_to_rgb(c.get('accent_color', '#ED1C24'))
    
    # Detect if we are using Template 4 (Pointing Woman on the right)
    bg_path = c.get('bg_image_path', '')
    is_template_4 = 'template_4' in bg_path
    is_template_bg = 'template' in bg_path or 'logo' in bg_path
    
    padding = int(w * 0.08)
    content_w = int(w * 0.55) if is_template_4 else int(w * 0.85)
    alignment = "left" if is_template_4 else "center"
    
    # If centering, x_pos is center. If left-aligned, x_pos is the left margin.
    text_x = padding if is_template_4 else w / 2
    
    # 1. Background Pattern (Subtle depth)
    if not c.get('bg_image_path'):
        d.rectangle([0, 0, w, h], fill="#FFFFFF")
        draw_geometric_pattern(f, (*primary, 20), type="dots")
    
    # 2. Content overlay for readability (Refined Glassmorphism)
    if is_template_4 and not is_template_bg:
        draw_glass_rect(f, (0, 0, content_w + padding, h), fill=(255, 255, 255, 200), blur_radius=8)

    # 3. Logo (Premium placement)
    logo_path = c.get('logo_path', 'logo/image.png')
    logo_pos = (padding + 100, 80) if is_template_4 else (w/2, 80)
    draw_logo(f, logo_path, logo_pos, size=(200, 80))
    
    # 4. Content Block (Dynamic Typography)
    curr_y = 280
    
    # 4. Content Block (Dynamic Typography)
    curr_y = 280
    
    # Calculate contrast dynamically because templates can be light or dark 
    base_bg_color = '#FFFFFF' if is_template_bg else c.get('bg_color', '#FFFFFF')
    contrast_text = "#1A1A1A" if get_brightness(base_bg_color) > 128 else "#FFFFFF"
    
    # Dynamic Headline
    max_h_h = int(h * 0.3)
    h_init = int(h * 0.08)
    headline = c.get('headline', 'BUILD THE FUTURE').upper()
    h_size = calculate_optimal_font_size(d, headline, c['default_font'], content_w, max_h_h, h_init)
    font_h = get_font(c['default_font'], h_size, bold=True)
    curr_y = draw_wrapped_text(d, headline, font_h, contrast_text, content_w, text_x, curr_y, alignment=alignment, line_height=0.95)
    
    # Tagline (Dynamic)
    if c.get('tagline'):
        curr_y += 20
        font_tag = get_font(c['default_font'], int(h * 0.035), bold=True)
        # Use primary for tagline if background is light, otherwise try accent
        tag_color = primary if get_brightness(base_bg_color) > 128 else accent
        curr_y = draw_wrapped_text(d, c['tagline'], font_tag, tag_color, content_w, text_x, curr_y, alignment=alignment, line_height=1.2)

    # 5. Professional Footer Items (Pills)
    footer_y = h - 220
    
    # Body Text (Dynamic)
    if c.get('body_text'):
        curr_y += 25
        max_h_b = footer_y - 20 - curr_y
        b_size = calculate_optimal_font_size(d, c['body_text'], c['default_font'], content_w, max_h_b, int(h * 0.028), min_size=20)
        font_body = get_font(c['default_font'], b_size)
        body_color = "#444444" if get_brightness(base_bg_color) > 128 else "#DDDDDD"
        curr_y = draw_wrapped_text(d, c['body_text'], font_body, body_color, content_w, text_x, curr_y, alignment=alignment, line_height=1.4)
    
    # 5. Professional Footer Items (Pills)
    draw_social_pills(d, c, w, h, h - 140, alignment="left" if is_template_4 else "center", padding=padding)

    # Branded accent strip at bottom
    draw_accent_line(d, (0, h-8), (w, h-8), primary, width=16)
    draw_accent_line(d, (0, h-8), (w*0.3, h-8), accent, width=16)

    # 6. Branded Accent Details
    bar_h = 10
    d.rectangle([0, h - bar_h, w, h], fill=primary)
    d.rectangle([0, h - bar_h - 4, w * 0.3, h - bar_h], fill=accent)

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
    is_template_bg = 'template' in c.get('bg_image_path', '') or 'logo' in c.get('bg_image_path', '')
    if not is_template_bg:
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

    # Main headline (Dynamic Contrast)
    base_bg_color = '#FFFFFF' if is_template_bg else c.get('bg_color', '#1A1A2E')
    text_color_h = "#1A1A1A" if get_brightness(base_bg_color) > 128 else "#FFFFFF"
    
    draw_wrapped_text(d, headline, font_h, text_color_h, w * 0.75,
                      padding_x, tag_y + 68,
                      alignment='left', line_height=1.05)

    # 6. Footer strip
    footer_h = int(h * 0.065)
    d.rectangle([0, h - footer_h, w, h], fill=(*primary, 230))
    font_f   = get_font(c['default_font'], 24, bold=True)
    # CTA / Website
    cta      = c.get('cta_text', 'www.codees-cm.com').lower()
    cta_w    = font_f.getlength(cta)
    d.text((w - padding_x - cta_w,  h - footer_h + (footer_h - 28) // 2), cta, font=font_f, fill='#FFFFFF')
    
    # Social Handle
    soc_text = "@codees_cm"
    d.text((padding_x, h - footer_h + (footer_h - 28) // 2), soc_text, font=font_f, fill='#FFFFFF')
def render_social_post(ctx):
    """Social Post v2: Cleancentered design, tailored for Template 2 (Quotes)."""
    f = ctx['flyer']
    d = ctx['draw']
    w = ctx['width']
    h = ctx['height']
    c = ctx['config']
    
    primary = hex_to_rgb(c.get('primary_color', '#0076BC'))
    secondary = hex_to_rgb(c.get('secondary_color', '#1A1A1A'))
    
    # Detect Template 2
    bg_path = c.get('bg_image_path', '')
    is_template_2 = 'template_2' in bg_path
    
    padding = int(w * 0.1)
    
    # 1. Background Pattern (Subtle dots for texture)
    if not bg_path:
        d.rectangle([0, 0, w, h], fill="#F8FAFC")
        draw_geometric_pattern(f, (*primary, 25), type="dots")
    
    # 2. Main Content Box
    if is_template_2:
        # Centered quote area
        curr_y = int(h * 0.35)
        text_w = int(w * 0.8)
        text_x = w / 2
    else:
        # Standard social post with image
        if 'image_path' in c and os.path.exists(c['image_path']):
            img_h = int(h * 0.5)
            img = Image.open(c['image_path'])
            img = resize_to_fill(img, w, img_h)
            f.paste(img, (0, 0))
            # Subtle gradient overlay on bottom of image
            overlay = Image.new('RGBA', (w, 120), (0,0,0,0))
            od = ImageDraw.Draw(overlay)
            for i in range(120): od.line([(0, i), (w, i)], fill=(0,0,0, int(100 * i/120)))
            f.paste(overlay, (0, img_h - 120), overlay)
            curr_y = img_h + 50
        else:
            curr_y = (h // 2) - 100
        
        text_w = w - 2*padding
        text_x = w / 2

    # Headline/Quote (Dynamic Scaling)
    max_h_h = int(h * 0.4)
    h_init = int(h * 0.08) if is_template_2 else int(h * 0.065)
    headline = c.get('headline', 'BE INSPIRED').upper()
    h_size = calculate_optimal_font_size(d, headline, c['default_font'], text_w, max_h_h, h_init)
    font_h = get_font(c['default_font'], h_size, bold=True)
    curr_y = draw_wrapped_text(d, headline, font_h, secondary, text_w, text_x, curr_y, alignment="center", line_height=0.95)
    
    # Tagline/Body (Dynamic)
    if c.get('body_text') or c.get('tagline'):
        curr_y += 30
        body_text = c.get('body_text', c.get('tagline', ''))
        # Limit body to avoid footer overlap
        max_h_b = (footer_y - 40 - curr_y) if not is_template_2 else (h - 60 - curr_y)
        b_size = calculate_optimal_font_size(d, body_text, c['default_font'], text_w, max_h_b, int(h * 0.032), min_size=18)
        font_body = get_font(c['default_font'], b_size)
        curr_y = draw_wrapped_text(d, body_text, font_body, primary, text_w, text_x, curr_y, alignment="center", line_height=1.4)

    # 3. Dynamic Branded Footer (Removed for Template 2 Quote Style)
    if not is_template_2:
        # Standard social post footer
        footer_y = h - 140
        cta_text = c.get('cta_text', 'www.codees-cm.com').upper()
        font_cta = get_font(c['default_font'], int(h * 0.025), bold=True)
        tw = font_cta.getlength(cta_text)
        d.text((w/2 - tw/2, footer_y), cta_text, font=font_cta, fill=secondary)
        # Accent Line
        d.rectangle([w/2 - 40, footer_y - 15, w/2 + 40, footer_y - 12], fill=primary)
        draw_social_pills(d, c, w, h, footer_y + 35, alignment="center")

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
    bg_path = c.get('bg_image_path', '')
    is_template_bg = 'template' in bg_path or 'logo' in bg_path
    if not bg_path:
        d.rectangle([0, 0, w, h], fill='#FFFFFF')

    # ── 2. Hero Photo (right side, clipped with diagonal) ──────────────────────
    photo_x = int(w * 0.30)   # photo starts here
    img_path = c.get('image_path', '')
    if not is_template_bg:
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
    if not is_template_bg:
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
    text_color_h = dark if is_template_bg else '#FFFFFF'
    for line in textwrap.wrap(headline, width=12):
        d.text((50, curr_y), line, font=font_h, fill=text_color_h)
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
    if not is_template_bg:
        draw_rotated_square(d, w - 60, 80, 70, 20, dark, 200)
        draw_rotated_square(d, w - 110, 130, 45, 35, dark, 150)
        draw_rotated_square(d, w - 40, 160, 30, 50, primary, 200)

    # ── 7. Dark bottom panel ───────────────────────────────────────────────────
    panel_y = int(h * 0.52)
    if not is_template_bg:
        d.rectangle([0, panel_y, w, h], fill=dark)

    # Centered sub-headline
    sub = c.get('sub_headline', 'ABSTRACT BUSINESS').upper()
    font_sub = get_font(c['default_font'], 52, bold=True)
    sub_w = font_sub.getlength(sub)
    text_color_sub = dark if is_template_bg else '#FFFFFF'
    d.text(((w - sub_w) / 2, panel_y + 40), sub, font=font_sub, fill=text_color_sub)

    # Sub-tagline
    tag = c.get('tagline', 'LOREM IPSUM DOLORES').upper()
    font_tag2 = get_font(c['default_font'], 26)
    tag_w = font_tag2.getlength(tag)
    d.text(((w - tag_w) / 2, panel_y + 108), tag, font=font_tag2, fill=primary)

    # Body text
    body = c.get('body_text', 'Join the fastest-growing tech community in Cameroon. We connect developers, designers, and entrepreneurs to create impact.')
    font_b = get_font(c['default_font'], 22)
    text_color_b = '#444444' if is_template_bg else '#CCCCCC'
    draw_wrapped_text(d, body, font_b, text_color_b, w * 0.76, w / 2, panel_y + 155, alignment='center', line_height=1.5)

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
        text_color_ft = dark if is_template_bg else '#FFFFFF'
        d.text((cx - it_w / 2, icon_y + r + 12), feat['title'], font=font_it, fill=text_color_ft)
        # Desc
        font_id = get_font(c['default_font'], 18)
        text_color_fc = '#666666' if is_template_bg else '#AAAAAA'
        draw_wrapped_text(d, feat.get('desc', ''), font_id, text_color_fc, col_w - 40, cx, icon_y + r + 46, alignment='center', line_height=1.35)

    # ── 9. Social footer strip ─────────────────────────────────────────────────
    footer_h = int(h * 0.08)
    footer_y = h - footer_h
    d.rectangle([0, footer_y, w, h], fill=primary)
    draw_social_pills(d, c, w, h, footer_y + (footer_h - 42) // 2, alignment="center")


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
    bg_path = c.get('bg_image_path', '')
    is_template_bg = 'template' in bg_path or 'logo' in bg_path
    if not bg_path:
        d.rectangle([0, 0, w, h], fill='#FFFFFF')

    # 2. Hero photo (top 55%)
    photo_h = int(h * 0.55)
    img_path = c.get('image_path', '')
    if not is_template_bg:
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
    if not is_template_bg:
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
    text_color_h = dark if is_template_bg else '#FFFFFF'
    for line in textwrap.wrap(headline, width=10):
        d.text((44, curr_y), line, font=font_h, fill=text_color_h)
        curr_y += int(font_h.size * 1.08)
    d.rectangle([44, curr_y + 6, 44 + 80, curr_y + 12], fill=accent)

    # 6. Top-right ornaments
    def draw_diamond(cx_, cy_, size_, color_):
        pts = [(cx_, cy_ - size_), (cx_ + size_, cy_), (cx_, cy_ + size_), (cx_ - size_, cy_)]
        d.polygon(pts, fill=color_)
    if not is_template_bg:
        draw_diamond(w - 55, 55, 48, (*dark, 200))
        draw_diamond(w - 100, 110, 30, (*dark, 140))
        draw_diamond(w - 32, 120, 22, (*primary, 220))

    # 7. Dark bottom panel
    panel_y = int(h * 0.52)
    if not is_template_bg:
        d.rectangle([0, panel_y, w, h], fill=dark)

    # Sub-headline centered
    sub      = c.get('sub_headline', c.get('headline', 'CODEES COMMUNITY')).upper()
    font_sub = get_font(c['default_font'], 46, bold=True)
    sub_w    = font_sub.getlength(sub)
    # Wrap if needed
    sub_lines = textwrap.wrap(sub, width=18)
    sy = panel_y + 30
    text_color_sub = dark if is_template_bg else '#FFFFFF'
    for sl in sub_lines:
        slw = font_sub.getlength(sl)
        d.text(((w - slw) / 2, sy), sl, font=font_sub, fill=text_color_sub)
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
    
    # Hide the button block if template bg is used, but still draw text maybe? Or draw button as is?
    # Actually button looks fine anywhere.
    d.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + 56], radius=8, fill=primary)
    tw2 = font_cta.getlength(cta_txt)
    d.text((cta_x + (cta_w - tw2) / 2, cta_y + 14), cta_txt, font=font_cta, fill='#FFFFFF')

    # 9. Social handles footer
    footer_h2 = int(h * 0.08)
    fy2       = h - footer_h2
    d.rectangle([0, fy2, w, h], fill=primary)
    draw_social_pills(d, c, w, h, fy2 + (footer_h2 - 42) // 2, alignment="center")

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
    
    # Smart Defaults for specific templates (All have white backgrounds)
    template_defaults = {
        'template_1': { # Marketing Agency
            'primary_color': '#0076BC', 
            'secondary_color': '#1A1A1A',
            'bg_color': '#FFFFFF'
        },
        'template_2': { # Social Post / Quote
            'primary_color': '#0076BC', 
            'secondary_color': '#1A1A1A',
            'bg_color': '#FFFFFF',
            'flyer_width': 1080,
            'flyer_height': 1080
        },
        'template_3': { # Zenith Modern / Stats
            'primary_color': '#0076BC', 
            'accent_color': '#ED1C24',
            'bg_color': '#FFFFFF'
        },
        'template_4': { # Codees Minimal / Person
            'primary_color': '#0076BC', 
            'accent_color': '#ED1C24',
            'bg_color': '#FFFFFF'
        }
    }
    
    # If template is specified, map it to template_id
    if 'template' in params:
        raw_name = str(params['template']).strip().lower()
        template_name = raw_name.replace(" ", "_")
        
        # Check for direct match or variations
        target_key = None
        if template_name in template_mapping:
            target_key = template_name
        elif f"template_{template_name}" in template_mapping:
            target_key = f"template_{template_name}"
        elif template_name in ['1', '2', '3', '4']:
            target_key = f"template_{template_name}"
            
        if target_key:
            config['template_id'] = template_mapping[target_key]
            
            # Apply Template Defaults if user hasn't overridden them
            if target_key in template_defaults:
                for k, v in template_defaults[target_key].items():
                    if k not in params: # Only apply if not sent by user
                        config[k] = v
        else:
            print(f"DEBUG: Template '{params['template']}' not found in mapping")
            
    tid = config.get('template_id')
    
    # Reverse mapping to auto-load background image if not set
    if not config.get('bg_image_path') and tid:
        reverse_mapping = {v: k for k, v in template_mapping.items()}
        mapped_template_name = reverse_mapping.get(tid)
        # Only auto-load if it's a 'template_N' image and not a 'logo' or other string
        if mapped_template_name and mapped_template_name.startswith('template_'):
            template_img_path = os.path.join(os.path.dirname(__file__), 'template', f"{mapped_template_name}.png")
            if os.path.exists(template_img_path):
                config['bg_image_path'] = template_img_path
    
    if isinstance(config.get('features'), str):
        try: config['features'] = json.loads(config['features'])
        except: pass

    width = int(config['flyer_width'])
    height = int(config['flyer_height'])
    
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

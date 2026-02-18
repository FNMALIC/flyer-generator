# Flyer Generator Flask API

A simple Flask REST API to generate customized flyer images (PNG) from parameters and images sent via HTTP requests.

## Installation

1. Clone the repository or download the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`.

## API Endpoint

### POST `/generate-flyer`

Returns the generated flyer as a PNG image directly in the response.

#### Parameters (multipart/form-data)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `image` | File | Yes | Main image to display on one side | - |
| `image_position` | String | No | "left" or "right" | "left" |
| `image_ratio` | Float | No | 0.0 - 1.0 (portion of width) | 0.5 |
| `flyer_width` | Int | No | Pixel width | 1200 |
| `flyer_height` | Int | No | Pixel height | 800 |
| `bg_type` | String | No | "color" or "image" | "color" |
| `bg_color` | String | No | Hex color code | "#FFFFFF" |
| `bg_image` | File | No | Image for text side background | - |
| `overlay_enabled` | Boolean | No | "true"/"false" | "false" |
| `overlay_color` | String | No | Hex color code | "#000000" |
| `overlay_opacity` | Float | No | 0.0 - 1.0 | 0.4 |
| `company_name` | String | No | Company name text | - |
| `company_font_size`| Int | No | Font size | 60 |
| `headline` | String | No | Headline text | - |
| `headline_font_size`| Int | No | Font size | 40 |
| `body_text` | String | No | Body text (\n for breaks) | - |
| `body_font_size` | Int | No | Font size | 24 |
| `contact_phone` | String | No | Phone number | - |
| `contact_email` | String | No | Email address | - |
| `contact_address` | String | No | Mailing address | - |
| `contact_website` | String | No | Website URL | - |

*Note: All colors should be hex strings (e.g., `#FF5733`). Fonts can be specified if the .ttf file exists on the server.*

## Example Usage

### Using `curl`

```bash
curl -X POST \
  -F "image=@your_main_image.jpg" \
  -F "company_name=Antigravity Tech" \
  -F "headline=Build Faster with AI" \
  -F "body_text=We provide state-of-the-art agentic solutions.\nJoin the revolution today!" \
  -F "bg_color=#F0F0F0" \
  -F "contact_email=hello@antigravity.ai" \
  http://localhost:5000/generate-flyer --output flyer.png
```

## Error Handling

The API returns JSON error responses with appropriate HTTP status codes (400 for missing input, 500 for server errors).

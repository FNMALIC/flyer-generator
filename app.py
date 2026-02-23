from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from flyer_generator import generate_flyer
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_files(file_paths):
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                app.logger.error(f"Error deleting file {path}: {e}")

@app.route('/templates', methods=['GET'])
def list_templates():
    """List available templates in the template folder."""
    try:
        template_dir = os.path.join(os.path.dirname(__file__), 'template')
        if not os.path.exists(template_dir):
            return jsonify({"templates": []})
        
        templates = []
        for file in os.listdir(template_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_name = os.path.splitext(file)[0]
                templates.append(template_name)
        
        return jsonify({"templates": sorted(templates)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-flyer', methods=['POST'])
def generate_flyer_endpoint():
    temp_files = []
    try:
        # Check for template selection first
        template_name = request.form.get('template')
        if template_name:
            # Use template from template folder
            template_path = os.path.join(os.path.dirname(__file__), 'template', f"{template_name}.png")
            if not os.path.exists(template_path):
                return jsonify({"error": f"Template '{template_name}' not found"}), 400
            img_path = template_path
        elif 'image' in request.files and request.files['image'].filename != '':
            # Use uploaded image
            main_image = request.files['image']
            if not allowed_file(main_image.filename):
                return jsonify({"error": "Invalid file type for 'image'"}), 400

            # Save main image
            img_filename = secure_filename(f"{uuid.uuid4()}_{main_image.filename}")
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            main_image.save(img_path)
            temp_files.append(img_path)
        else:
            # Use default image.png as fallback
            img_path = os.path.join(os.path.dirname(__file__), 'image.png')
            if not os.path.exists(img_path):
                return jsonify({"error": "No template, image, or default image found"}), 400

        # Background image (optional)
        bg_image_path = None
        if 'bg_image' in request.files:
            bg_image = request.files['bg_image']
            if bg_image and bg_image.filename != '' and allowed_file(bg_image.filename):
                bg_filename = secure_filename(f"bg_{uuid.uuid4()}_{bg_image.filename}")
                bg_image_path = os.path.join(app.config['UPLOAD_FOLDER'], bg_filename)
                bg_image.save(bg_image_path)
                temp_files.append(bg_image_path)

        # Extract parameters
        params = {
            'image_path': img_path,
        }
        if bg_image_path:
            params['bg_image_path'] = bg_image_path

        # Layout & General
        basic_params = [
            'layout_type', 'image_position', 'image_ratio', 'flyer_width', 'flyer_height',
            'bg_type', 'bg_color', 'gradient_start', 'gradient_end',
            'overlay_enabled', 'overlay_color', 'overlay_opacity',
            'padding', 'section_spacing', 'text_alignment', 'line_height'
        ]
        for key in basic_params:
            if key in request.form:
                params[key] = request.form[key]

        # Text Sections
        text_keys = [
            'company_name', 'company_font', 'company_font_size', 'company_font_color',
            'headline', 'headline_font', 'headline_font_size', 'headline_font_color',
            'body_text', 'body_font', 'body_font_size', 'body_font_color',
            'contact_phone', 'contact_email', 'contact_address', 'contact_website',
            'contact_font', 'contact_font_size', 'contact_font_color',
            'show_cta', 'cta_bg_color', 'cta_text_color'
        ]
        for key in text_keys:
            if key in request.form:
                params[key] = request.form[key]

        # Generate flyer
        try:
            img_io = generate_flyer(params)
        except Exception as e:
            app.logger.error(f"Generation error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Image processing error: {str(e)}"}), 500

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        app.logger.error(f"Server error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cleanup_files(temp_files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
